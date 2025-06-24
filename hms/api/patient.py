import frappe


@frappe.whitelist()
def get_previous_patient_visits(patient, exclude_visit=None, limit=10, offset=0):
	filters = {"patient": patient}
	if exclude_visit:
		filters["name"] = ["!=", exclude_visit]

	visits = frappe.get_all(
		"Patient Visit",
		filters=filters,
		fields=[
			"name",
			"visit_date",
			"follow_up",
			"doctor",
			"remarks",
			"medication_details"
		],
		order_by="visit_date desc",
		limit_page_length=limit,
		limit_start=offset
	)
	if not visits:
		return []

	# Enrich each visit with lab reports
	for v in visits:
		v["lab_reports"] = frappe.get_all(
			"Lab Report",
			filters={
				"visit_reference": v["name"]
			},
			fields=["name", "report_type", "received_on", "report_file"]
		)
	return visits

import frappe
from frappe.utils import today

@frappe.whitelist()
def get_latest_op_expiry(patient):
	result = frappe.get_all(
		"OP Record",
		filters={"patient": patient},
		fields=["valid_till"],
		order_by="valid_till desc",
		limit=1
	)
	return result[0].valid_till if result else None

@frappe.whitelist()
def get_latest_follow_up(patient):
	result = frappe.get_all(
		"Patient Visit",
		filters={"patient": patient},
		fields=["follow_up"],
		order_by="visit_date desc",
		limit=1
	)
	return result[0].follow_up if result and result[0].follow_up else None

@frappe.whitelist()
def get_previous_treatments(ip_record, start=0, page_length=5, exclude_treatment=None):
	start = int(start)
	page_length = int(page_length)
	filters = {"in_patient": ip_record}
	if exclude_treatment:
		filters["name"] = ["!=", exclude_treatment]
 
	treatments = frappe.get_all(
		"In Patient Treatment",
		filters=filters,
		fields=["name", "date", "doctor", "diagnosis_update", "medications_given"],
		order_by="date desc",
		limit_start=start,
		limit_page_length=page_length
	)

	for t in treatments:
		vitals = frappe.get_all(
			"Vitals Entry",
			filters={"parent": t["name"], "parenttype": "In Patient Treatment"},
			fields=["time", "temperature", "pulse", "blood_pressure", "respiratory_rate", "recorded_by"],
			order_by="time asc"
		)
		t["vitals"] = vitals

	return treatments
