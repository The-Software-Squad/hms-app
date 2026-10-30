import frappe
from frappe.utils import nowdate

from hms.workflows import CLINICAL_ROLES, checked_doc, page_args, require_roles


@frappe.whitelist()
def get_previous_patient_visits(patient, exclude_visit=None, limit=10, offset=0):
	require_roles(CLINICAL_ROLES)
	checked_doc("Patient", patient)
	limit, offset = page_args(limit, offset)
	filters = {"patient": patient}
	if exclude_visit:
		filters["name"] = ["!=", exclude_visit]
	visits = frappe.get_list(
		"Patient Visit",
		filters=filters,
		fields=["name", "visit_date", "department", "follow_up", "doctor", "remarks", "medication_details"],
		order_by="visit_date desc, creation desc",
		limit_page_length=limit,
		limit_start=offset,
	)
	if not visits:
		return []
	doctors = {
		d.name: d.practitioner_name
		for d in frappe.get_list(
			"Healthcare Practitioner",
			filters={"name": ["in", list({v.doctor for v in visits if v.doctor})]},
			fields=["name", "practitioner_name"],
			limit_page_length=100,
		)
	}
	reports = frappe.get_list(
		"Lab Report",
		filters={"visit_reference": ["in", [v.name for v in visits]]},
		fields=["name", "visit_reference", "report_type", "received_on", "report_file"],
		limit_page_length=1000,
	)
	by_visit = {}
	for report in reports:
		by_visit.setdefault(report.visit_reference, []).append(report)
	for visit in visits:
		visit["doctor_name"] = doctors.get(visit.doctor, visit.doctor)
		visit["lab_reports"] = by_visit.get(visit.name, [])
	return visits


@frappe.whitelist()
def get_latest_follow_up(patient):
	checked_doc("Patient", patient)
	return frappe.db.get_value("Patient", patient, "follow_up")


@frappe.whitelist()
def get_latest_validity_expiry(patient):
	checked_doc("Patient", patient)
	windows = frappe.get_list(
		"Fee Validity",
		filters={"patient": patient, "status": "Active", "valid_till": [">=", nowdate()]},
		fields=["valid_till"],
		order_by="valid_till desc",
		limit_page_length=1,
	)
	return windows[0].valid_till if windows else None


@frappe.whitelist()
def get_previous_treatments(ip_record, start=0, page_length=5, exclude_treatment=None):
	require_roles(CLINICAL_ROLES)
	checked_doc("IP Record", ip_record)
	page_length, start = page_args(page_length, start)
	filters = {"in_patient": ip_record}
	if exclude_treatment:
		filters["name"] = ["!=", exclude_treatment]
	treatments = frappe.get_list(
		"In Patient Treatment",
		filters=filters,
		fields=["name", "date", "doctor", "diagnosis_update", "medications_given"],
		order_by="date desc, creation desc",
		limit_start=start,
		limit_page_length=page_length,
	)
	for treatment in treatments:
		doc = checked_doc("In Patient Treatment", treatment.name)
		treatment["vitals"] = [v.as_dict() for v in doc.vitals]
	return treatments
