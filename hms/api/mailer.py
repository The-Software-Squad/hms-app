import frappe
from hms.utils.icalender import generate_icalender_from_medicine_schedule
@frappe.whitelist()
def send_medication_mail(visit):
	'''Generate ICalendar and send medication schedule via email.'''
	# Get the mediciation schedule child table.
	patient_visit = frappe.get_doc("Patient Visit", visit)
	patient = frappe.get_doc("Patient", patient_visit.patient)
	patient_email = patient.patient_email
	medication_schedule = patient_visit.medication_schedule
	if not medication_schedule:
		frappe.throw("No medication schedule found for this visit.")
	# Generate the iCalendar string.
	icalender_string = generate_icalender_from_medicine_schedule(medication_schedule=medication_schedule)
	frappe.sendmail(
		recipients=patient_email,
		subject=f"Medication Schedule for {patient.patient_name}",
		message="Please find your medication schedule attached.",
		attachments=[{
			"fname": "medication_schedule.ics",
			"fcontent": icalender_string,
		}]
	)
	frappe.msgprint(f"Medication schedule sent to {patient_email}.")
	return {
		"message": f"Medication schedule sent to {patient_email}.",
		"icalender_string": icalender_string
	}