import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from hms.departures import validate_departure_fields
from hms.workflows import (
	CLINICAL_ROLES,
	active_patient,
	atomic_action,
	current_rows,
	immutable,
	lock,
	require_roles,
	validate_dates,
)


class IPRecord(Document):
	def validate(self):
		validate_departure_fields(self)
		immutable(self, ("patient", "admission_date"))
		old = self.get_doc_before_save()
		if not old:
			active_patient(self.patient)
		if not self.bed:
			frappe.throw(_("Select an available bed before saving the admission."))
		if getdate(self.admission_date) > getdate(nowdate()):
			frappe.throw(_("Admission date cannot be in the future."))
		if (
			self.status == "Discharged"
			and (not old or old.status != "Discharged")
			and not (frappe.flags.hms_discharge or frappe.flags.hms_departure)
		):
			frappe.throw(
				_("Finalize a Discharge Summary or record the actual departure to close the admission.")
			)
		if old and old.status == "Discharged" and self.status != "Discharged" and not frappe.flags.hms_reopen:
			frappe.throw(_("Use Reopen Admission with a reason."))
		if old and old.status == "Discharged" and self.status == "Discharged":
			immutable(self, ("bed", "practitioner", "discharge_date", "discharge_summary"))
		validate_dates(self.admission_date, self.discharge_date, "Discharge Date")
		lock("Patient", self.patient)
		if self.status != "Discharged" and current_rows(
			"IP Record",
			{"patient": self.patient, "name": ["!=", self.name], "status": ["!=", "Discharged"]},
			["name"],
		):
			frappe.throw(_("This patient already has an active admission."))
		beds = sorted({b for b in [old.bed if old else None, self.bed] if b})
		for name in beds:
			lock("Bed", name)
		for name in beds:
			bed = frappe.get_doc("Bed", name, for_update=True)
			owner = bed.current_admission
			if name == self.bed and self.status != "Discharged":
				other = current_rows(
					"IP Record",
					{"bed": name, "status": ["!=", "Discharged"], "name": ["!=", self.name]},
					["name"],
				)
				if (
					other
					or (owner and owner != self.name)
					or (bed.current_patient and bed.current_patient != self.patient)
				):
					frappe.throw(_("Bed {0} is already occupied.").format(name))

		self.doctor_user = frappe.db.get_value("Healthcare Practitioner", self.practitioner, "user")
		self.doctor = frappe.db.get_value("Healthcare Practitioner", self.practitioner, "practitioner_name")

	def on_update(self):
		old = self.get_doc_before_save()
		for name in sorted({b for b in [old.bed if old else None, self.bed] if b}):
			bed = frappe.get_doc("Bed", name, for_update=True)
			if name == self.bed and self.status != "Discharged":
				frappe.db.set_value(
					"Bed",
					name,
					{"current_patient": self.patient, "current_admission": self.name},
					update_modified=False,
				)
			elif bed.current_admission == self.name or (
				not bed.current_admission and old and old.bed == name and bed.current_patient == old.patient
			):
				frappe.db.set_value(
					"Bed", name, {"current_patient": None, "current_admission": None}, update_modified=False
				)
		wards = {
			frappe.db.get_value("Bed", name, "ward")
			for name in [self.bed, self.get_doc_before_save().bed if self.get_doc_before_save() else None]
			if name
		}
		for ward in wards:
			if ward:
				frappe.db.set_value(
					"Ward",
					ward,
					"total_occupied",
					frappe.db.count("Bed", {"ward": ward, "current_patient": ["is", "set"]}),
					update_modified=False,
				)

	def on_trash(self):
		frappe.throw(_("Admissions are retained for clinical history; discharge them instead of deleting."))

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def reopen(self, reason):
		require_roles(CLINICAL_ROLES)
		self.check_permission("write")
		if self.status != "Discharged" or not reason or not reason.strip():
			frappe.throw(_("A discharged admission and a reopening reason are required."))
		self.status, self.reopen_reason = "Under Treatment", reason.strip()
		self.discharge_date, self.discharge_summary = None, None
		self.departure_record, self.departure_outcome, self.departed_on = None, None, None
		frappe.flags.hms_reopen = True
		try:
			self.save()
		finally:
			frappe.flags.hms_reopen = False
		return self.name
