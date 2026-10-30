from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, getdate, nowdate

from hms.workflows import CANCELLED_VISIT, current_rows, lock, update_patient_dates


class FeeValidity(Document):
	def validate(self):
		if cint(self.max_visits) < 0 or cint(self.visited) < 0:
			frappe.throw(_("Visit counts cannot be negative."))
		self.update_status()

	def update_status(self):
		if self.status == "Cancelled":
			return
		if self.valid_till and getdate(self.valid_till) < getdate(nowdate()):
			self.status = "Expired"
		elif cint(self.visited) >= cint(self.max_visits):
			self.status = "Completed"
		else:
			self.status = "Active"


def _get_validity_settings(practitioner=None):
	settings = frappe.get_single("Hospital Settings")
	enabled = bool(settings.enable_free_follow_ups)
	days, visits = cint(settings.valid_days), cint(settings.max_visits)
	if practitioner:
		doc = frappe.get_cached_doc("Healthcare Practitioner", practitioner)
		policy = doc.get("followup_policy") or "Inherit"
		if policy == "Disabled":
			enabled = False
		elif policy == "Enabled" or doc.enable_free_follow_ups:
			enabled = True
		if policy == "Enabled" or doc.enable_free_follow_ups:
			days, visits = cint(doc.valid_days or days), cint(doc.max_visits or visits)
	if enabled and (days < 1 or visits < 1):
		frappe.throw(_("Enabled free follow-ups require positive validity days and visit count."))
	return enabled, days, visits


def manage_fee_validity_on_visit(doc, method=None):
	if doc.status == CANCELLED_VISIT:
		return
	# A shared patient lock serializes first-window creation and consumption.
	lock("Patient", doc.patient)
	enabled, days, maximum = _get_validity_settings(doc.doctor)
	if enabled:
		windows = current_rows(
			"Fee Validity",
			filters={
				"patient": doc.patient,
				"practitioner": doc.doctor,
				# Display status is relative to today; entitlement is relative to the visit date.
				"status": ["in", ["Active", "Expired", "Completed"]],
				"start_date": ["<=", doc.visit_date],
				"valid_till": [">=", doc.visit_date],
			},
			fields=["name"],
			order_by="start_date desc, creation desc",
		)
		for window in windows:
			lock("Fee Validity", window.name)
			fv = frappe.get_doc("Fee Validity", window.name, for_update=True)
			if cint(fv.visited) >= cint(fv.max_visits):
				continue
			if not any(r.visit == doc.name for r in fv.ref_visits):
				fv.append("ref_visits", {"visit": doc.name})
				fv.visited = len(fv.ref_visits)
				fv.save(ignore_permissions=True)
			doc.db_set("fee_validity", fv.name, update_modified=False)
			update_patient_dates(doc.patient)
			return
		fv = frappe.get_doc(
			{
				"doctype": "Fee Validity",
				"patient": doc.patient,
				"practitioner": doc.doctor,
				"department": doc.department,
				"patient_visit": doc.name,
				"start_date": getdate(doc.visit_date),
				"valid_till": getdate(doc.visit_date) + timedelta(days=days - 1),
				"max_visits": maximum,
				"visited": 0,
				"status": "Active",
			}
		).insert(ignore_permissions=True)
		doc.db_set("fee_validity", fv.name, update_modified=False)
	from hms.billing import ensure_visit_invoice

	ensure_visit_invoice(doc)
	update_patient_dates(doc.patient)


def validate_visit_validity_release(visit):
	if not visit.fee_validity:
		return
	lock("Patient", visit.patient)
	lock("Fee Validity", visit.fee_validity)
	fv = frappe.get_doc("Fee Validity", visit.fee_validity, for_update=True)
	if fv.patient_visit == visit.name:
		if fv.ref_visits:
			frappe.throw(
				_(
					"This visit has used follow-ups; cancel those follow-ups before cancelling its initial visit."
				)
			)
	return fv


def release_visit_validity(visit):
	fv = validate_visit_validity_release(visit)
	if not fv:
		return
	if fv.patient_visit == visit.name:
		fv.status = "Cancelled"
	else:
		fv.set("ref_visits", [row for row in fv.ref_visits if row.visit != visit.name])
		fv.visited = len(fv.ref_visits)
	fv.save(ignore_permissions=True)
	visit.db_set("fee_validity", None, update_modified=False)


def update_validity_status():
	# Only windows whose dates have passed need a daily write; completed counts are handled on save.
	for row in frappe.get_all(
		"Fee Validity",
		filters={"status": ["in", ["Active", "Completed"]], "valid_till": ["<", nowdate()]},
		fields=["name", "patient"],
	):
		frappe.db.set_value("Fee Validity", row.name, "status", "Expired", update_modified=False)
		update_patient_dates(row.patient)
