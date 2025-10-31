# Copyright (c) 2025, HMS
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate


class PatientAppointment(Document):
    def validate(self):
        self._validate_times()
        self._validate_practitioner_active()
        self._validate_availability()
        self._validate_conflicts()

    def on_update(self):
        # Auto-create Patient Visit when moved to Checked In and not already linked
        try:
            old = self.get_doc_before_save()
        except Exception:
            old = None

        if self.status == "Checked In" and not self.patient_visit:
            # if transitioned or fresh set
            if (old and old.status != self.status) or not old:
                self._create_patient_visit()

    def _validate_times(self):
        if not self.appointment_date:
            frappe.throw(_("Appointment Date is required."))
        if not self.start_time:
            frappe.throw(_("Start Time is required."))
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            frappe.throw(_("End Time must be after Start Time."))

    def _validate_practitioner_active(self):
        if not self.practitioner:
            return
        active = frappe.db.get_value("Healthcare Practitioner", self.practitioner, "active")
        if active is not None and int(active) != 1:
            frappe.throw(_("Selected practitioner is not active."))

    def _validate_availability(self):
        """Ensure the appointment fits within any schedule time slot on the day."""
        if not (self.practitioner and self.appointment_date and self.start_time):
            return
        weekday = getdate(self.appointment_date).strftime("%A")  # Monday..Sunday

        schedules = frappe.get_all(
            "Practitioner Schedule",
            filters={"practitioner": self.practitioner},
            fields=["name", "effective_from", "effective_upto"],
        )

        if not schedules:
            frappe.throw(_("No schedule found for the selected practitioner."))

        fits_any = False
        for sch in schedules:
            if sch.effective_from and getdate(self.appointment_date) < getdate(sch.effective_from):
                continue
            if sch.effective_upto and getdate(self.appointment_date) > getdate(sch.effective_upto):
                continue

            slots = frappe.get_all(
                "Practitioner Schedule Time Slot",
                filters={"parent": sch.name, "parenttype": "Practitioner Schedule", "day_of_week": weekday},
                fields=["start_time", "end_time"],
            )
            for slot in slots:
                if self.start_time >= slot.start_time and (not self.end_time or self.end_time <= slot.end_time):
                    fits_any = True
                    break
            if fits_any:
                break

        if not fits_any:
            frappe.throw(
                _("Healthcare Practitioner {0} not available on {1}").format(self.practitioner, frappe.format(getdate(self.appointment_date)))
            )

    def _validate_conflicts(self):
        """No other overlapping appointment for same practitioner, date, and time window."""
        filters = {
            "name": ("!=", self.name or ""),
            "practitioner": self.practitioner,
            "appointment_date": self.appointment_date,
            "status": ("in", ["Scheduled", "Checked In", "In Service"]),
        }
        existing = frappe.get_all(
            "Patient Appointment",
            filters=filters,
            fields=["name", "start_time", "end_time"],
        )
        for ap in existing:
            # Overlap check: start < other_end and end > other_start
            self_end = self.end_time or self.start_time
            ap_end = ap.end_time or ap.start_time
            if self.start_time < ap_end and self_end > ap.start_time:
                frappe.throw(_("Conflicts with appointment {0}.").format(ap.name))

    def _create_patient_visit(self):
        visit = frappe.new_doc("Patient Visit")
        visit.patient = self.patient
        if self.practitioner:
            visit.doctor = self.practitioner
        if self.department:
            visit.department = self.department
        visit.visit_date = self.appointment_date
        visit.status = "Checked In"
        visit.flags.ignore_mandatory = False
        visit.insert(ignore_permissions=True)
        self.db_set("patient_visit", visit.name, update_modified=False)
