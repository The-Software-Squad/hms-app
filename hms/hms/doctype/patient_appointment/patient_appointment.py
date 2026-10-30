from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from hms.workflows import (
	active_patient,
	appointment_status_for_visit,
	atomic_action,
	current_rows,
	immutable,
	lock,
	time_value,
)

ACTIVE = ("Scheduled", "Checked In", "In Service")


class PatientAppointment(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if self.patient_visit and (not old or not old.patient_visit):
			frappe.throw(_("The visit link is assigned by Check In and cannot be entered manually."))
		if old and old.patient_visit:
			immutable(
				self,
				(
					"patient",
					"practitioner",
					"appointment_date",
					"start_time",
					"end_time",
					"department",
					"patient_visit",
					"follow_up_visit",
				),
			)
			if self.status != old.status and self.status in ("Scheduled", "Checked In"):
				frappe.throw(
					_("A checked-in appointment cannot be rebooked; cancel and create a new appointment.")
				)
		if (
			self.follow_up_visit
			and frappe.db.get_value("Patient Visit", self.follow_up_visit, "patient") != self.patient
		):
			frappe.throw(_("The follow-up consultation must belong to this patient."))
		if self.status in ACTIVE:
			active_patient(self.patient)
		practitioner = frappe.get_doc("Healthcare Practitioner", self.practitioner)
		self.department = self.department or practitioner.department
		if not self.department:
			frappe.throw(_("Set the appointment department or the practitioner's department before booking."))
		self.start_time = time_value(self.start_time)
		if not self.end_time:
			end = datetime.combine(getdate(self.appointment_date), self.start_time) + timedelta(minutes=30)
			if end.date() != getdate(self.appointment_date):
				frappe.throw(_("Appointments must end on the same date."))
			self.end_time = end.time()
		self.end_time = time_value(self.end_time)
		if self.end_time <= self.start_time:
			frappe.throw(_("End Time must be after Start Time."))
		if self.status in ACTIVE:
			practitioner.validate()
			if not practitioner.active:
				frappe.throw(_("Selected practitioner is not active."))
			lock("Patient", self.patient)
			lock("Healthcare Practitioner", self.practitioner)
			self._validate_availability()
			self._validate_conflicts()
		if self.status in ("In Service", "Completed", "Closed Early") and not self.patient_visit:
			frappe.throw(_("Check the patient in before starting or completing the appointment."))
		if self.patient_visit:
			visit_status = frappe.db.get_value("Patient Visit", self.patient_visit, "status")
			expected = appointment_status_for_visit(visit_status)
			if self.status == "No Show":
				frappe.throw(_("This patient has checked in. Record a cancellation instead of a no-show."))
			if expected in ("Completed", "Closed Early", "Cancelled") and self.status != expected:
				frappe.throw(_("The consultation is closed. Create a new appointment for another visit."))
			if self.status not in (expected, "Cancelled"):
				frappe.throw(
					_("Appointment progress is set by the linked consultation. Refresh the appointment.")
				)
			if self.status == "Cancelled" and expected != "Cancelled":
				frappe.get_doc("Patient Visit", self.patient_visit).validate_cancellation_dependencies()

	def _validate_availability(self):
		weekday = getdate(self.appointment_date).strftime("%A")
		schedules = frappe.get_all(
			"Practitioner Schedule",
			filters={"practitioner": self.practitioner},
			fields=["name", "effective_from", "effective_upto"],
		)
		for schedule in schedules:
			if schedule.effective_from and getdate(self.appointment_date) < getdate(schedule.effective_from):
				continue
			if schedule.effective_upto and getdate(self.appointment_date) > getdate(schedule.effective_upto):
				continue
			for slot in frappe.get_all(
				"Practitioner Schedule Time Slot",
				filters={
					"parent": schedule.name,
					"parenttype": "Practitioner Schedule",
					"day_of_week": weekday,
				},
				fields=["start_time", "end_time"],
			):
				if (
					time_value(slot.start_time)
					<= self.start_time
					< self.end_time
					<= time_value(slot.end_time)
				):
					return
		frappe.throw(_("The appointment must fit within the practitioner's schedule."))

	def _validate_conflicts(self):
		appointments = current_rows(
			"Patient Appointment",
			filters={
				"name": ["!=", self.name or ""],
				"practitioner": self.practitioner,
				"appointment_date": self.appointment_date,
				"status": ["in", ACTIVE],
			},
			fields=["name", "start_time", "end_time"],
		)
		for appointment in appointments:
			start = time_value(appointment.start_time)
			end = (
				time_value(appointment.end_time)
				if appointment.end_time
				else (datetime.combine(getdate(self.appointment_date), start) + timedelta(minutes=30)).time()
			)
			if self.start_time < end and self.end_time > start:
				frappe.throw(_("Conflicts with appointment {0}.").format(appointment.name))

	def on_update(self):
		if self.follow_up_visit:
			state = "Closed" if self.status == "Completed" else "Scheduled"
			if self.status in ("Cancelled", "No Show", "Closed Early"):
				other = frappe.db.exists(
					"Patient Appointment",
					{
						"follow_up_visit": self.follow_up_visit,
						"name": ["!=", self.name],
						"status": ["in", ACTIVE],
					},
				)
				state = "Scheduled" if other else "Pending"
			frappe.db.set_value(
				"Patient Visit", self.follow_up_visit, "follow_up_status", state, update_modified=False
			)
		if self.status == "Checked In" and not self.patient_visit:
			self._create_patient_visit()
		elif self.patient_visit and self.status in ("Cancelled", "No Show"):
			visit = frappe.get_doc("Patient Visit", self.patient_visit)
			if visit.status == "Completed":
				frappe.throw(_("A completed consultation cannot be marked cancelled or no show."))
			if visit.status != "Cancelled / No Show":
				visit.status = "Cancelled / No Show"
				visit.save(ignore_permissions=True)

	def _create_patient_visit(self):
		# Unique visit.appointment plus the appointment row lock make retries idempotent.
		existing = frappe.db.get_value("Patient Visit", {"appointment": self.name}, "name")
		if existing:
			self.db_set("patient_visit", existing, update_modified=False)
			return
		visit = frappe.get_doc(
			{
				"doctype": "Patient Visit",
				"patient": self.patient,
				"doctor": self.practitioner,
				"department": self.department,
				"visit_date": self.appointment_date,
				"status": "Checked In",
				"appointment": self.name,
			}
		).insert(ignore_permissions=True)
		self.db_set("patient_visit", visit.name, update_modified=False)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def check_in(self):
		self.check_permission("write")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status not in ("Scheduled", "Checked In"):
			frappe.throw(_("Only a scheduled appointment can be checked in."))
		self.status = "Checked In"
		self.save()
		return self.patient_visit
