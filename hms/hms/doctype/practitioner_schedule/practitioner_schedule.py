# Copyright (c) 2025, HMS
# For license information, please see license.txt

from frappe.model.document import Document
from frappe import _


class PractitionerSchedule(Document):
    def validate(self):
        # Require at least one time slot
        if not self.get("time_slots"):
            from frappe import throw

            throw(_("Please add at least one Time Slot."))

        # Each slot must have end > start
        for row in self.time_slots:
            if row.end_time and row.start_time and row.end_time <= row.start_time:
                from frappe import throw

                throw(_("End Time must be after Start Time for {0}.").format(row.day_of_week))

