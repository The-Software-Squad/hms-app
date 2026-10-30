"""Shared guards for HMS workflows. Locks live until the surrounding Frappe transaction ends."""

import frappe
from frappe import _
from frappe.utils import cint, get_time, getdate, nowdate

CLINICAL_ROLES = {"Doctor", "System Manager"}
FRONT_DESK_ROLES = {"Receptionist", "Doctor", "System Manager"}
PHARMACY_ROLES = {"Pharmacist", "System Manager"}
BILLING_ROLES = {"Receptionist", "Pharmacist", "System Manager"}
CANCELLED_VISIT = "Cancelled / No Show"


def appointment_status_for_visit(status):
	return {
		"Scheduled": "Scheduled",
		"Checked In": "Checked In",
		"Completed": "Completed",
		"Closed Early": "Closed Early",
		CANCELLED_VISIT: "Cancelled",
	}.get(status, "In Service")


def require_roles(roles):
	if frappe.session.user == "Guest" or not set(frappe.get_roles()).intersection(roles):
		frappe.throw(_("You are not permitted to perform this action."), frappe.PermissionError)


def checked_doc(doctype, name, permission="read", for_update=False):
	doc = frappe.get_doc(doctype, name, for_update=for_update)
	doc.check_permission(permission)
	return doc


def lock(doctype, name):
	if not frappe.db.get_value(doctype, name, "name", for_update=True):
		frappe.throw(_("{0} {1} does not exist.").format(doctype, name), frappe.DoesNotExistError)


def current_rows(doctype, filters, fields, order_by="name"):
	"""Internal workflow state after a lock: bypass a stale repeatable-read snapshot.

	Callers perform authorization separately; never use this for user-facing lists.
	"""
	return frappe.db.get_values(doctype, filters, fields, as_dict=True, order_by=order_by, for_update=True)


def page_args(limit, start=0):
	return max(1, min(cint(limit), 100)), max(0, cint(start))


def active_patient(name):
	patient = frappe.get_doc("Patient", name)
	if patient.status == "Disabled":
		frappe.throw(_("The selected patient is disabled."))
	if patient.get("merged_into"):
		frappe.throw(_("This patient was merged into {0}.").format(patient.merged_into))
	return patient


def validate_dates(start, end, label):
	if start and end and getdate(end) < getdate(start):
		frappe.throw(_("{0} cannot be before {1}.").format(label, start))


def time_value(value):
	if value is None or value == "":
		frappe.throw(_("A time value is required."))
	return get_time(value)


def immutable(doc, fields, message=None):
	old = doc.get_doc_before_save()
	if not old:
		return
	for field in fields:
		if str(old.get(field) or "") != str(doc.get(field) or ""):
			frappe.throw(
				message
				or _("{0} cannot be changed after creation; cancel and create a new record.").format(field)
			)


def update_patient_dates(patient):
	"""Maintain operational dates on writes, never as a side effect of viewing a form."""
	visits = frappe.get_all(
		"Patient Visit",
		filters={"patient": patient, "status": ["!=", CANCELLED_VISIT]},
		fields=["follow_up"],
		order_by="visit_date desc, creation desc",
		limit_page_length=1,
	)
	follow_up = visits[0].follow_up if visits else None
	admissions = frappe.get_all(
		"Discharge Summary",
		filters={"patient": patient, "status": "Finalized"},
		fields=["follow_up", "discharge_date"],
		order_by="discharge_date desc, creation desc",
		limit_page_length=1,
	)
	if admissions and admissions[0].follow_up:
		latest_visit = frappe.db.get_value(
			"Patient Visit",
			{"patient": patient, "status": ["!=", CANCELLED_VISIT]},
			"visit_date",
			order_by="visit_date desc",
		)
		if not latest_visit or getdate(admissions[0].discharge_date) >= getdate(latest_visit):
			follow_up = admissions[0].follow_up
	windows = frappe.get_all(
		"Fee Validity",
		filters={"patient": patient, "status": "Active", "valid_till": [">=", nowdate()]},
		fields=["valid_till"],
		order_by="valid_till desc",
		limit_page_length=1,
	)
	frappe.db.set_value(
		"Patient",
		patient,
		{"follow_up": follow_up, "validity_expiring_on": windows[0].valid_till if windows else None},
		update_modified=False,
	)


def atomic_action(fn):
	"""A caught posting failure must not leave partial stock/financial writes behind."""
	from functools import wraps

	@wraps(fn)
	def wrapped(*args, **kwargs):
		point = "hms_action_" + frappe.generate_hash(length=10)
		frappe.db.savepoint(point)
		try:
			result = fn(*args, **kwargs)
		except frappe.QueryDeadlockError:
			# InnoDB may have aborted the entire transaction, invalidating this savepoint.
			# Frappe rolls back the request and reports a retryable transaction conflict.
			raise
		except Exception:
			frappe.db.rollback(save_point=point)
			raise
		else:
			frappe.db.release_savepoint(point)
			return result

	return wrapped
