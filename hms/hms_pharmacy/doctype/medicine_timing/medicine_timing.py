import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

from hms.workflows import time_value


class MedicineTiming(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if old and frappe.db.exists("Medication Schedule", {"timing": self.name}):
			before = [(time_value(r.start_time), time_value(r.end_time)) for r in old.timings]
			after = [(time_value(r.start_time), time_value(r.end_time)) for r in self.timings]
			if cint(self.interval or 1) != cint(old.interval or 1) or before != after:
				frappe.throw(
					_(
						"This timing is used by prescriptions. Create a new timing instead of changing historical schedules."
					)
				)
		self.interval = cint(self.interval or 1)
		if self.interval < 1 or not self.timings:
			frappe.throw(_("Set a positive interval and at least one timing window."))
		seen = set()
		for row in self.timings:
			row.start_time, row.end_time = time_value(row.start_time), time_value(row.end_time)
			if row.start_time >= row.end_time or row.start_time in seen:
				frappe.throw(_("Medication timing windows must be positive and have distinct start times."))
			seen.add(row.start_time)
