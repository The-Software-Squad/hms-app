import hashlib
import json

import frappe
from frappe import _
from frappe.utils import now_datetime, validate_email_address

from hms.utils.icalender import generate_icalender_from_medicine_schedule
from hms.workflows import CLINICAL_ROLES, atomic_action, checked_doc, lock, require_roles


def prescription_version(visit):
	rows = [
		{key: row.get(key) for key in ("medicine", "dose", "timing", "start_date", "duration_days")}
		for row in visit.medication_schedule
	]
	return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()


@frappe.whitelist()
def preview_medication_calendar(visit):
	require_roles(CLINICAL_ROLES)
	doc = checked_doc("Patient Visit", visit)
	checked_doc("Patient", doc.patient)
	return generate_icalender_from_medicine_schedule(
		doc.medication_schedule, f"{doc.name}:{prescription_version(doc)}"
	)


@frappe.whitelist(methods=["POST"])
@atomic_action
def send_medication_mail(visit):
	require_roles(CLINICAL_ROLES)
	lock("Patient Visit", visit)
	doc = checked_doc("Patient Visit", visit, "write", for_update=True)
	patient = checked_doc("Patient", doc.patient, for_update=True)
	if doc.status not in ("Prescription Given", "Completed"):
		frappe.throw(_("Save the prescription with status Prescription Given or Completed before sending."))
	email = validate_email_address(patient.patient_email or "", throw=True)
	if not email or "," in email or ";" in email or "\n" in email:
		frappe.throw(_("A single valid patient email address is required."))
	version = prescription_version(doc)
	key = hashlib.sha256(f"{doc.name}:{version}:{email}".encode()).hexdigest()
	existing = frappe.db.get_value(
		"HMS Medication Delivery", {"delivery_key": key}, ["name", "status"], as_dict=True, for_update=True
	)
	if existing:
		return {"delivery": existing.name, "status": existing.status, "duplicate": True}
	calendar = generate_icalender_from_medicine_schedule(doc.medication_schedule, f"{doc.name}:{version}")
	delivery = frappe.get_doc(
		{
			"doctype": "HMS Medication Delivery",
			"delivery_key": key,
			"patient_visit": doc.name,
			"patient": patient.name,
			"recipient": email,
			"requested_by": frappe.session.user,
			"requested_on": now_datetime(),
			"status": "Queued",
		}
	).insert(ignore_permissions=True)
	# sendmail queues transactionally; its queue retries and reports provider failures.
	queue = frappe.sendmail(
		recipients=[email],
		subject=f"Medication Schedule for {patient.patient_name}",
		message="Please find your medication schedule attached.",
		attachments=[{"fname": "medication_schedule.ics", "fcontent": calendar}],
		reference_doctype=delivery.doctype,
		reference_name=delivery.name,
	)
	if not queue:
		frappe.throw(
			_("No email queue was created. Check the outgoing email account and recipient before retrying.")
		)
	delivery.db_set("email_queue", queue.name)
	return {"delivery": delivery.name, "status": "Queued", "duplicate": False}


def update_delivery_statuses():
	for delivery in frappe.get_all(
		"HMS Medication Delivery",
		filters={"status": "Queued"},
		fields=["name", "email_queue"],
		limit_page_length=500,
	):
		queue = delivery.email_queue or frappe.db.get_value(
			"Email Queue",
			{"reference_doctype": "HMS Medication Delivery", "reference_name": delivery.name},
			"name",
		)
		if not queue:
			continue
		status = frappe.db.get_value("Email Queue", queue, "status")
		mapped = {
			"Sent": "Sent",
			"Error": "Failed",
			"Not Sent": "Queued",
			"Sending": "Queued",
			"Partially Sent": "Failed",
		}.get(status, "Queued")
		frappe.db.set_value(
			"HMS Medication Delivery",
			delivery.name,
			{"email_queue": queue, "status": mapped},
			update_modified=False,
		)
