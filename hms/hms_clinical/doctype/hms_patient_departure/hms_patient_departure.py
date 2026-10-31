import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, getdate, now_datetime

from hms.workflows import (
	CLINICAL_ROLES,
	FRONT_DESK_ROLES,
	atomic_action,
	current_rows,
	immutable,
	lock,
	require_roles,
)


class HMSPatientDeparture(Document):
	def validate(self):
		old = self.get_doc_before_save()
		immutable(self, ("source_doctype", "source_name"))
		if self.source_doctype not in ("Patient Visit", "IP Record"):
			frappe.throw(_("Select a consultation or admission."))
		source = frappe.get_doc(self.source_doctype, self.source_name)
		source.check_permission("read")
		self.patient = source.patient
		if get_datetime(self.departed_on) > now_datetime() or getdate(self.departed_on) < getdate(
			source.get("visit_date") or source.admission_date
		):
			frappe.throw(_("Departure must be between the care start date and now."))
		if not (self.reason or "").strip():
			frappe.throw(_("Record why the patient left."))
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_departure:
			frappe.throw(_("Use Finalize Departure."))
		if not frappe.flags.hms_departure:
			for field in ("finalized_by", "finalized_on", "review_status"):
				if str(self.get(field) or "") != str(
					old.get(field) or "" if old else ("Not Required" if field == "review_status" else "")
				):
					frappe.throw(_("Departure review and audit fields are assigned by the workflow."))
		if old and old.status == "Finalized":
			for field in self.meta.get_valid_columns():
				if field in ("modified", "modified_by", "review_status"):
					continue
				if str(self.get(field) or "") != str(old.get(field) or ""):
					frappe.throw(
						_("Finalized departures are retained unchanged; add a comment for further context.")
					)
		if (
			old
			and not set(frappe.get_roles()).intersection(CLINICAL_ROLES)
			and self.clinical_notes != old.clinical_notes
		):
			frappe.throw(_("Only clinical staff can change clinical notes."), frappe.PermissionError)
		if self.clinical_notes and not set(frappe.get_roles()).intersection(CLINICAL_ROLES):
			frappe.throw(_("Only clinical staff can enter clinical notes."), frappe.PermissionError)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def finalize(self):
		require_roles(FRONT_DESK_ROLES)
		self.check_permission("write")
		stored = frappe.db.get_value(
			self.doctype, self.name, ["source_doctype", "source_name", "patient"], as_dict=True
		)
		lock("Patient", stored.patient)
		lock(stored.source_doctype, stored.source_name)
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Finalized":
			return self.source_name
		source = frappe.get_doc(self.source_doctype, self.source_name, for_update=True)
		source.check_permission("write")
		is_visit = self.source_doctype == "Patient Visit"
		if source.departure_record or source.status in (
			"Completed",
			"Cancelled / No Show",
			"Closed Early",
			"Discharged",
		):
			frappe.throw(_("The care record is already closed. Create a new visit for further care."))
		if self.outcome != "Left Before Seen" or not is_visit:
			require_roles(CLINICAL_ROLES)
		if is_visit:
			if self.outcome == "Admission Cancelled":
				frappe.throw(_("Admission Cancelled is only available for admissions."))
			if self.outcome == "Left Before Seen":
				if (
					source.status not in ("Scheduled", "Checked In")
					or source.remarks
					or source.medication_details
					or source.medication_schedule
				):
					frappe.throw(_("Care has started. Record a departure during care with clinical review."))
				source.validate_cancellation_dependencies()
				source.status = "Cancelled / No Show"
			else:
				if not self.clinical_notes:
					frappe.throw(_("Record the clinical assessment, advice and any further care needed."))
				source.status = "Closed Early"
			pending = current_rows(
				"Lab Report",
				{"visit_reference": source.name, "status": ["not in", ["Reviewed", "Cancelled"]]},
				["name"],
			)
			if pending:
				if not self.responsible_practitioner or not self.review_due_on:
					frappe.throw(_("Assign a pending-results owner and review due date before closing care."))
				owner = frappe.get_doc("Healthcare Practitioner", self.responsible_practitioner)
				if not owner.active or getdate(self.review_due_on) < getdate(self.departed_on):
					frappe.throw(_("Select an active results owner and a due date on or after departure."))
			self.review_status = "Pending" if pending else "Not Required"
		else:
			if self.outcome == "Left Before Seen":
				frappe.throw(_("Use Admission Cancelled before inpatient treatment has started."))
			if self.outcome == "Admission Cancelled" and current_rows(
				"In Patient Treatment", {"in_patient": source.name}, ["name"]
			):
				frappe.throw(_("Treatment has started. Record the actual departure during care."))
			if not self.clinical_notes:
				frappe.throw(_("Record the clinical assessment and advice before closing the admission."))
			source.status, source.discharge_date = "Discharged", getdate(self.departed_on)
		self.status, self.finalized_by, self.finalized_on = "Finalized", frappe.session.user, now_datetime()
		source.departure_record, source.departure_outcome, source.departed_on = (
			self.name,
			self.outcome,
			self.departed_on,
		)
		frappe.flags.hms_departure = True
		try:
			self.save()
			source.save(ignore_permissions=True)
		finally:
			frappe.flags.hms_departure = False
		return source.name

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def resolve_review(self):
		require_roles(CLINICAL_ROLES)
		self.check_permission("write")
		stored = frappe.db.get_value(self.doctype, self.name, ["source_doctype", "source_name"], as_dict=True)
		lock(stored.source_doctype, stored.source_name)
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status != "Finalized" or self.review_status not in ("Pending", "Resolved"):
			frappe.throw(_("There is no finalized pending-results review to resolve."))
		if current_rows(
			"Lab Report",
			{"visit_reference": self.source_name, "status": ["not in", ["Reviewed", "Cancelled"]]},
			["name"],
		):
			frappe.throw(
				_("Review received results and cancel unperformed requests before resolving this review.")
			)
		self.review_status = "Resolved"
		frappe.flags.hms_departure = True
		try:
			self.save()
		finally:
			frappe.flags.hms_departure = False
		return self.name

	def on_trash(self):
		if self.status == "Finalized":
			frappe.throw(_("Finalized departures must retain their history."))
