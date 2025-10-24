import frappe
from hms.utils import has_active_out_patient_record


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
			"department",
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
		# Fetch doctor name for display (if available)
		if v.get("doctor"):
			try:
				v["doctor_name"] = frappe.db.get_value("Employee", v["doctor"], "employee_name") or v["doctor"]
			except Exception:
				v["doctor_name"] = v["doctor"]
		else:
			v["doctor_name"] = None

		v["lab_reports"] = frappe.get_all(
			"Lab Report",
			filters={
				"visit_reference": v["name"]
			},
			fields=["name", "report_type", "received_on", "report_file"]
		)
	return visits


@frappe.whitelist()
def has_active_out_patient(patient: str) -> bool:
	"""Return True if patient has an active Out Patient (child) record.

	This is a thin wrapper over utils for convenient client-side checks.
	"""
	if not patient:
		return False
	try:
		return bool(has_active_out_patient_record(patient))
	except Exception:
		return False

from frappe.utils import today

@frappe.whitelist()
def get_latest_op_expiry(patient):
	"""Return the latest Out Patient expiry date from Patient's child table.

	Falls back to None if no rows present or dates missing.
	"""
	if not patient:
		return None
	try:
		p = frappe.get_doc("Patient", patient)
		latest = None
		for row in getattr(p, "op_records", []) or []:
			row_to = row.get("to") if isinstance(row, dict) else getattr(row, "to", None)
			if row_to and (latest is None or row_to > latest):
				latest = row_to
		return latest
	except Exception:
		return None

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
