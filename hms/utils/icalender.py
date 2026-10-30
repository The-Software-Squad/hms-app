"""Calendar generation from the saved, validated prescription; duration is elapsed days."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from zoneinfo import ZoneInfo

import frappe
from frappe import _
from frappe.utils import cint, get_system_timezone, get_time, getdate
from icalendar import Alarm, Calendar, Event


def ensure_time(value):
	return get_time(value)


def get_scheduled_days(start_date, interval, duration):
	interval, duration = cint(interval or 1), cint(duration)
	if not start_date or interval < 1 or not 1 <= duration <= 366:
		frappe.throw(_("Provide a start date, a positive interval and a duration between 1 and 366 days."))
	return [getdate(start_date) + timedelta(days=offset) for offset in range(0, duration, interval)]


def validate_medication_schedule(rows):
	for row in rows:
		if not row.medicine or not row.dose or not row.timing:
			frappe.throw(_("Each medication needs a medicine, dose and timing."))
		timing = frappe.get_doc("Medicine Timing", row.timing)
		get_scheduled_days(row.start_date, timing.interval, row.duration_days)
		if not timing.timings:
			frappe.throw(_("Medicine Timing {0} has no time windows.").format(timing.name))
		for slot in timing.timings:
			if (
				not slot.start_time
				or not slot.end_time
				or get_time(slot.start_time) >= get_time(slot.end_time)
			):
				frappe.throw(_("Medication time windows must end after they start."))


def generate_icalender_from_medicine_schedule(medication_schedule, version="prescription"):
	if not medication_schedule:
		frappe.throw(_("No medication schedule found for this visit."))
	validate_medication_schedule(medication_schedule)
	cal = Calendar()
	cal.add("prodid", "-//HMS//Medication Schedule//EN")
	cal.add("version", "2.0")
	cal.add("method", "PUBLISH")
	grouped = defaultdict(list)
	zone = ZoneInfo(get_system_timezone())
	for row in medication_schedule:
		timing = frappe.get_doc("Medicine Timing", row.timing)
		medicine = frappe.get_cached_value("Medicine", row.medicine, "label")
		for day in get_scheduled_days(row.start_date, timing.interval, row.duration_days):
			for slot in timing.timings:
				grouped[(day, get_time(slot.start_time), get_time(slot.end_time))].append(
					f"{medicine} ({row.dose})"
				)
	for (day, start, end), medicines in sorted(grouped.items()):
		event = Event()
		identity = f"{version}:{day}:{start}:{end}"
		event.add("uid", sha256(identity.encode()).hexdigest() + "@hms")
		event.add("dtstamp", datetime.now(timezone.utc))
		event.add("dtstart", datetime.combine(day, start, tzinfo=zone))
		event.add("dtend", datetime.combine(day, end, tzinfo=zone))
		event.add("summary", "Take " + ", ".join(medicines))
		event.add("description", "\n".join(medicines))
		alarm = Alarm()
		alarm.add("action", "DISPLAY")
		alarm.add("description", "Medication reminder")
		alarm.add("trigger", timedelta())
		event.add_component(alarm)
		cal.add_component(event)
	return cal.to_ical().decode("utf-8")
