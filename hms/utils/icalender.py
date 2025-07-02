from collections import defaultdict
import frappe
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta, time

# Defensive conversion from timedelta to time
def ensure_time(t):
	if isinstance(t, timedelta):
		return (datetime.min + t).time()
	return t 

def get_scheduled_days(start_date, interval, duration):
	"""
	Returns a list of dates based on:
	- start_date: the first day to take the medicine
	- interval: number of days between doses (e.g., 1 = daily, 2 = every other day)
	- duration: total number of doses to take
	"""
	interval = interval or 1  # default to daily if not specified
	return [start_date + timedelta(days=i * interval) for i in range(duration)]

def generate_icalender_from_medicine_schedule(medication_schedule):
	"""
	Generate an iCalendar string from a medicine schedule.

	:param medication_schedule: List of dictionaries containing medicine schedule details.
	:return: iCalendar string.
	"""
	cal = Calendar()
	cal.add('prodid', '-//HMS//EN')
	cal.add('version', '2.0')
	cal.add('method', 'PUBLISH')
	grouped_alarms = defaultdict(list)
	for schedule in medication_schedule:
		# Get medicine timing doc
		timing_doc = frappe.get_doc("Medicine Timing", schedule.timing)
		medicine = frappe.get_doc("Medicine", schedule.medicine)
		if not timing_doc or not timing_doc.timings or not medicine:
			continue

		# Extract medicine info
		dose = schedule.dose
		start_date = schedule.start_date
		duration = int(schedule.duration_days or 1)
		interval = timing_doc.interval or 1

		# Get scheduled days for this medicine
		scheduled_days = get_scheduled_days(start_date, interval, duration)
	
		for timing in timing_doc.timings:
			if not timing.start_time or not timing.end_time:
				continue
			
			for scheduled_day in scheduled_days:
				# Create a key for grouping alarms
				current_date = scheduled_day
				key = (current_date, timing.start_time, timing.end_time)
				grouped_alarms[key].append({
					'medicine_name': medicine.label,
					'dose': dose,
				})

	# Create events for each scheduled day and time
	for (event_date, event_time, event_end_time), medicines in grouped_alarms.items():
		event_time = ensure_time(event_time)
		event_end_time = ensure_time(event_end_time)
		event_start = datetime.combine(event_date, event_time)
		event_end = datetime.combine(event_date, event_end_time)
		# Take medicine(dose), medicine(dose), ...
		summary = 'Take ' + ', '.join([f"{med['medicine_name']}({med['dose']})" for med in medicines])
		description = '\n'.join([f"{med['medicine_name']} - Dose: {med['dose']}" for med in medicines])
  
		event = Event()
		event.add('summary', summary)
		event.add('dtstart', event_start)
		event.add('dtend', event_end)
		event.add('description', description)
		
		alarm = Alarm()
		alarm.add('action', 'DISPLAY')
		alarm.add('description', f"Reminder: {summary}")
		alarm.add('trigger', timedelta(minutes=0))
		event.add_component(alarm)
		cal.add_component(event)
	
	return cal.to_ical().decode('utf-8')
