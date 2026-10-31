import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

from hms.departures import validate_departure_fields
from hms.utils.icalender import validate_medication_schedule
from hms.workflows import (
	CANCELLED_VISIT,
	CLINICAL_ROLES,
	active_patient,
	appointment_status_for_visit,
	current_rows,
	immutable,
	lock,
	update_patient_dates,
	validate_dates,
)

CLINICAL_FIELDS = ("remarks", "medication_details", "medication_schedule")


class PatientVisit(Document):
	def validate(self):
		validate_departure_fields(self)
		if not self.is_new():
			lock(self.doctype, self.name)
		if self.is_new() and self.status != CANCELLED_VISIT:
			active_patient(self.patient)
		immutable(self, ("patient", "doctor", "visit_date", "department", "appointment"))
		doctor = frappe.get_doc("Healthcare Practitioner", self.doctor)
		if self.is_new() and self.status != CANCELLED_VISIT:
			doctor.validate()
		self.department = self.department or doctor.department
		self.doctor_user = doctor.user
		if self.is_new() and self.status != CANCELLED_VISIT and not doctor.active:
			frappe.throw(_("Select an active practitioner."))
		if not self.department:
			frappe.throw(_("A department is required."))
		old = self.get_doc_before_save()
		if not old and (self.fee_validity or self.invoice):
			frappe.throw(_("Fee eligibility and invoices are assigned by the visit workflow."))
		if old:
			immutable(self, ("fee_validity", "invoice", "completed_by", "completed_on"))
		clinical_user = bool(set(frappe.get_roles()).intersection(CLINICAL_ROLES))
		if not clinical_user:
			if self.status not in ("Scheduled", "Checked In", CANCELLED_VISIT) and (
				not old or self.status != old.status
			):
				frappe.throw(_("Only clinical staff can change consultation status."), frappe.PermissionError)
			for name in CLINICAL_FIELDS:
				if self.get(name) and (not old or self.get(name) != old.get(name)):
					frappe.throw(
						_("Only clinical staff can change consultation notes or prescriptions."),
						frappe.PermissionError,
					)
		if old and old.status in ("Completed", "Closed Early", CANCELLED_VISIT) and self.status != old.status:
			frappe.throw(_("Completed or cancelled visits cannot be reopened; create a new visit."))
		if old and old.status in ("Completed", "Closed Early"):
			changed = any(self.get(name) != old.get(name) for name in ("remarks", "medication_details"))
			changed = changed or (
				(getdate(self.follow_up) if self.follow_up else None)
				!= (getdate(old.follow_up) if old.follow_up else None)
			)
			keys = ("medicine", "dose", "timing", "start_date", "duration_days", "quantity")
			changed = changed or [[str(r.get(k) or "") for k in keys] for r in self.medication_schedule] != [
				[str(r.get(k) or "") for k in keys] for r in old.medication_schedule
			]
			if changed and (not self.correction_reason or self.correction_reason == old.correction_reason):
				frappe.throw(_("Provide a new correction reason to amend a closed consultation."))
		validate_dates(self.visit_date, self.follow_up, "Follow-up")
		# Serialize first use against medicine-master edits; the master freezes once referenced.
		for medicine in sorted({row.medicine for row in self.medication_schedule if row.medicine}):
			lock("Medicine", medicine)
		validate_medication_schedule(self.medication_schedule)
		if (
			self.status == "Closed Early"
			and (not old or old.status != "Closed Early")
			and not frappe.flags.hms_departure
		):
			frappe.throw(_("Use Record Departure to close care early."))
		if self.status == CANCELLED_VISIT:
			self.validate_cancellation_dependencies()
		if self.status == "Completed":
			if not self.remarks:
				frappe.throw(_("Record the consultation findings before completing the visit."))
			if frappe.db.exists(
				"Lab Report", {"visit_reference": self.name, "status": ["not in", ["Reviewed", "Cancelled"]]}
			):
				frappe.throw(_("Review or cancel pending lab reports before completing the visit."))
			if not old or old.status != "Completed":
				self.completed_by, self.completed_on = frappe.session.user, now_datetime()
		if self.appointment:
			appointment = frappe.get_doc("Patient Appointment", self.appointment)
			if (
				appointment.patient != self.patient
				or appointment.practitioner != self.doctor
				or getdate(appointment.appointment_date) != getdate(self.visit_date)
			):
				frappe.throw(_("The visit does not match its appointment."))

	def on_update(self):
		from hms.hms_reception.doctype.fee_validity.fee_validity import release_visit_validity

		if self.status == CANCELLED_VISIT:
			release_visit_validity(self)
			from hms.billing import void_source_invoice

			void_source_invoice(self.doctype, self.name, "Consultation cancelled")
		if self.appointment:
			state = appointment_status_for_visit(self.status)
			frappe.db.set_value(
				"Patient Appointment",
				self.appointment,
				{"status": state, "patient_visit": self.name},
				update_modified=False,
			)
			follow_up_visit = frappe.db.get_value("Patient Appointment", self.appointment, "follow_up_visit")
			if follow_up_visit:
				frappe.db.set_value(
					"Patient Visit",
					follow_up_visit,
					"follow_up_status",
					"Closed"
					if state == "Completed"
					else ("Pending" if state in ("Cancelled", "Closed Early") else "Scheduled"),
					update_modified=False,
				)
		update_patient_dates(self.patient)

	def validate_cancellation_dependencies(self):
		if current_rows(
			"Lab Report",
			{"visit_reference": self.name, "status": ["not in", ["Reviewed", "Cancelled"]]},
			["name"],
		):
			frappe.throw(
				_(
					"Resolve the linked lab reports before cancelling: cancel unperformed requests or have clinical staff review received results."
				)
			)
		remaining = frappe.db.sql(
			"""select coalesce(sum(case when m.transaction_type='Return' then -r.med_quantity else r.med_quantity end),0)
			from `tabOut Medical Item` r join `tabMeds Out` m on m.name=r.parent
			where m.patient_visit=%s and m.status='Posted' and r.parenttype='Meds Out' FOR UPDATE""",
			(self.name,),
		)[0][0]
		if remaining > 0:
			frappe.throw(
				_(
					"This visit has posted medicines that have not been returned. Review dispensing before cancelling the visit."
				)
			)
		from hms.billing import validate_source_invoice_cancellation
		from hms.hms_reception.doctype.fee_validity.fee_validity import validate_visit_validity_release

		validate_visit_validity_release(self)
		validate_source_invoice_cancellation(self.doctype, self.name)

	def on_trash(self):
		frappe.throw(_("Cancel visits instead of deleting clinical history."))
