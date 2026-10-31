import frappe
from frappe import _
from frappe.model.document import Document

from hms.workflows import lock, time_value, validate_dates


class PractitionerSchedule(Document):
	def validate(self):
		lock("Healthcare Practitioner", self.practitioner)
		validate_dates(self.effective_from, self.effective_upto, "Effective Upto")
		if not self.time_slots:
			frappe.throw(_("Add at least one time slot."))
		by_day = {}
		for row in self.time_slots:
			if not row.day_of_week:
				frappe.throw(_("Select a weekday for every time slot."))
			row.start_time, row.end_time = time_value(row.start_time), time_value(row.end_time)
			if row.end_time <= row.start_time:
				frappe.throw(_("End Time must be after Start Time."))
			for start, end in by_day.setdefault(row.day_of_week, []):
				if row.start_time < end and row.end_time > start:
					frappe.throw(_("Time slots on the same weekday must not overlap."))
			by_day[row.day_of_week].append((row.start_time, row.end_time))
