import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

from hms.workflows import (
	CLINICAL_ROLES,
	atomic_action,
	immutable,
	lock,
	require_roles,
	update_patient_dates,
	validate_dates,
)


class DischargeSummary(Document):
	def validate(self):
		require_roles(CLINICAL_ROLES)
		immutable(self, ("in_patient", "patient"))
		admission = frappe.get_doc("IP Record", self.in_patient, for_update=True)
		admission.check_permission("read")
		if self.patient and self.patient != admission.patient:
			frappe.throw(_("The summary patient must match the admission."))
		self.patient = admission.patient
		self.practitioner = self.practitioner or admission.practitioner
		self.by_doctor = frappe.db.get_value("Healthcare Practitioner", self.practitioner, "employee")
		validate_dates(admission.admission_date, self.discharge_date, "Discharge Date")
		validate_dates(self.discharge_date, self.follow_up, "Follow-up")
		if getdate(self.discharge_date) > getdate(nowdate()):
			frappe.throw(_("Discharge date cannot be in the future."))
		old = self.get_doc_before_save()
		if (
			self.status == "Finalized"
			and (not old or old.status != "Finalized")
			and not frappe.flags.hms_finalizing
		):
			frappe.throw(_("Use Finalize Discharge to complete discharge."))
		if old and old.status == "Finalized":
			immutable(self, ("status", "discharge_date", "practitioner", "finalized_by", "finalized_on"))
			if any(
				self.get(k) != old.get(k)
				for k in ("final_diagnosis", "discharge_notes", "condition_at_discharge", "follow_up")
			):
				if not self.correction_reason or self.correction_reason == old.correction_reason:
					frappe.throw(_("Provide a new reason for correcting the finalized summary."))

	def on_update(self):
		if self.status == "Finalized":
			update_patient_dates(self.patient)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def finalize(self):
		require_roles(CLINICAL_ROLES)
		self.check_permission("write")
		lock("Patient", self.patient)
		lock("IP Record", self.in_patient)
		admission = frappe.get_doc("IP Record", self.in_patient, for_update=True)
		if admission.status == "Discharged":
			if admission.discharge_summary == self.name:
				return admission.name
			frappe.throw(_("This admission already has a finalized discharge."))
		if self.status == "Finalized":
			frappe.throw(_("Create a new discharge summary after reopening an admission."))
		self.status, self.finalized_by, self.finalized_on = "Finalized", frappe.session.user, now_datetime()
		frappe.flags.hms_finalizing = True
		frappe.flags.hms_discharge = True
		try:
			self.save()
			admission.status = "Discharged"
			admission.discharge_date, admission.discharge_summary = self.discharge_date, self.name
			admission.save(ignore_permissions=True)
		finally:
			frappe.flags.hms_finalizing = False
			frappe.flags.hms_discharge = False
		return admission.name

	def on_trash(self):
		if self.status == "Finalized":
			frappe.throw(_("A finalized discharge summary cannot be deleted."))
