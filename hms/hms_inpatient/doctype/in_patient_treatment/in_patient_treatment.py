import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import getdate, nowdate

from hms.workflows import CLINICAL_ROLES, immutable, lock, require_roles, time_value


class InPatientTreatment(Document):
	def autoname(self):
		self.name = make_autoname(f"{self.in_patient}-CARE-.###")

	def validate(self):
		require_roles(CLINICAL_ROLES)
		immutable(self, ("in_patient", "patient", "date"))
		lock("IP Record", self.in_patient)
		admission = frappe.get_doc("IP Record", self.in_patient, for_update=True)
		if self.is_new() and admission.departure_record:
			frappe.throw(
				_("This admission has a recorded departure. Reopen it with a reason before adding treatment.")
			)
		admission.check_permission("read")
		if self.patient and self.patient != admission.patient:
			frappe.throw(_("The treatment patient does not match the admission."))
		self.patient = admission.patient
		if getdate(self.date) < getdate(admission.admission_date) or getdate(self.date) > getdate(nowdate()):
			frappe.throw(_("Treatment date must be between admission and today."))
		if admission.discharge_date and getdate(self.date) > getdate(admission.discharge_date):
			frappe.throw(_("Treatment cannot be recorded after discharge."))
		self.practitioner = self.practitioner or admission.practitioner
		self.doctor = frappe.db.get_value("Healthcare Practitioner", self.practitioner, "practitioner_name")
		if self.is_new():
			self.recorded_by = frappe.session.user
		else:
			immutable(self, ("recorded_by",))
		for vital in self.vitals:
			vital.time = time_value(vital.time)
			if vital.is_new():
				vital.recorded_by = frappe.session.user
			else:
				old = frappe.db.get_value("Vitals Entry", vital.name, "recorded_by")
				if old:
					vital.recorded_by = old
			for field in ("temperature", "pulse", "respiratory_rate"):
				if vital.get(field) is not None and vital.get(field) < 0:
					frappe.throw(_("Vital measurements cannot be negative; verify the units and value."))

	def on_trash(self):
		frappe.throw(_("Treatment history cannot be deleted; record a correction instead."))
