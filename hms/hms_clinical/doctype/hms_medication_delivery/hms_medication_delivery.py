import frappe
from frappe import _
from frappe.model.document import Document

from hms.workflows import CLINICAL_ROLES, atomic_action, checked_doc, lock, require_roles


class HMSMedicationDelivery(Document):
	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def refresh_status(self):
		require_roles(CLINICAL_ROLES)
		self.check_permission("read")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		queue = self.email_queue or frappe.db.get_value(
			"Email Queue", {"reference_doctype": self.doctype, "reference_name": self.name}, "name"
		)
		if queue:
			status = frappe.db.get_value("Email Queue", queue, "status")
			mapped = {"Sent": "Sent", "Error": "Failed", "Partially Sent": "Failed"}.get(status, "Queued")
			self.db_set({"status": mapped, "email_queue": queue}, update_modified=False)
		return self.status

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def retry(self):
		require_roles(CLINICAL_ROLES)
		self.check_permission("read")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		visit = checked_doc("Patient Visit", self.patient_visit, "write")
		patient = checked_doc("Patient", self.patient)
		from hashlib import sha256

		from hms.api.mailer import prescription_version

		key = sha256(
			f"{visit.name}:{prescription_version(visit)}:{patient.patient_email}".encode()
		).hexdigest()
		if key != self.delivery_key or visit.status not in ("Prescription Given", "Completed"):
			frappe.throw(
				_(
					"The patient email or prescription changed. Preview and send the current saved prescription instead."
				)
			)
		if not self.email_queue:
			frappe.throw(
				_("No linked email queue exists; ask an administrator to check the outgoing email account.")
			)
		lock("Email Queue", self.email_queue)
		queue = frappe.db.get_value(
			"Email Queue",
			self.email_queue,
			["status", "reference_doctype", "reference_name"],
			as_dict=True,
			for_update=True,
		)
		if queue.reference_doctype != self.doctype or queue.reference_name != self.name:
			frappe.throw(_("The queue does not belong to this delivery."))
		if queue.status != "Error":
			frappe.throw(_("Only a failed email queue can be retried."))
		frappe.db.set_value("Email Queue", self.email_queue, "status", "Not Sent")
		self.db_set("status", "Queued")
		return self.status
