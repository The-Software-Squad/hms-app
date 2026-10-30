import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

from hms.workflows import CANCELLED_VISIT, CLINICAL_ROLES, immutable, lock, validate_dates


def validate_private_attachment(url, report=None):
	if not url:
		return
	if not url.startswith("/private/files/") or any(c in url for c in ['"', "'", "<", ">", "\n", "\r", "\\"]):
		frappe.throw(_("Upload a private report file; external or public URLs are not accepted."))
	files = frappe.get_all(
		"File",
		filters={"file_url": url, "is_private": 1},
		fields=["name", "attached_to_doctype", "attached_to_name"],
	)
	for candidate in files:
		if (
			report
			and (candidate.attached_to_doctype or candidate.attached_to_name)
			and (candidate.attached_to_doctype != "Lab Report" or candidate.attached_to_name != report)
		):
			continue
		file = frappe.get_doc("File", candidate.name)
		if file.has_permission("read"):
			return file.name
	frappe.throw(
		_(
			"Upload an accessible private file for this lab report; files attached to other records cannot be reused."
		),
		frappe.PermissionError,
	)


class LabReport(Document):
	def validate(self):
		immutable(self, ("visit_reference", "patient"))
		lock("Patient Visit", self.visit_reference)
		visit = frappe.get_doc("Patient Visit", self.visit_reference)
		visit.check_permission("read")
		if self.is_new() and visit.status in ("Completed", "Closed Early", CANCELLED_VISIT):
			frappe.throw(
				_("New lab requests require an active consultation. Create a new visit for further care.")
			)
		if self.patient and self.patient != visit.patient:
			frappe.throw(_("Report patient must match the consultation visit."))
		self.patient = visit.patient
		validate_dates(visit.visit_date, self.requested_on, "Requested On")
		validate_dates(self.requested_on, self.received_on, "Received On")
		if self.received_on and getdate(self.received_on) > getdate(nowdate()):
			frappe.throw(_("Received On cannot be in the future."))
		self.flags.hms_report_file = validate_private_attachment(self.report_file, self.name)
		if self.status in ("Received", "Reviewed") and not (self.received_on and self.report_file):
			frappe.throw(_("A received report needs its received date and private report file."))
		old = self.get_doc_before_save()
		if self.status == "Reviewed":
			if not set(frappe.get_roles()).intersection(CLINICAL_ROLES):
				frappe.throw(_("Only clinical staff may review results."), frappe.PermissionError)
			if not old or old.status != "Reviewed":
				self.reviewed_by, self.reviewed_on = frappe.session.user, now_datetime()
		if old and old.status == "Reviewed":
			immutable(self, ("status", "report_file", "received_on", "reviewed_by", "reviewed_on"))

	def on_update(self):
		if self.report_file:
			name = self.flags.hms_report_file
			frappe.db.set_value(
				"File",
				name,
				{
					"attached_to_doctype": "Lab Report",
					"attached_to_name": self.name,
					"attached_to_field": "report_file",
				},
				update_modified=False,
			)

	def on_trash(self):
		if self.status == "Reviewed" or frappe.db.get_value(
			"Patient Visit", self.visit_reference, "departure_record"
		):
			frappe.throw(_("Reviewed lab reports must be retained."))
