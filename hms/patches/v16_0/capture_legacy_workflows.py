"""Identify pre-ledger records before new status columns receive their draft defaults."""
import frappe
from frappe.utils import now

KEY = "hms_legacy_workflow_snapshot"


def execute():
	doctypes = [
		doctype
		for doctype in ("Meds In take", "Meds Out", "Payment Recipit")
		if frappe.db.table_exists(doctype) and not frappe.db.has_column(doctype, "status")
	]
	if doctypes:
		frappe.db.set_default(KEY, frappe.as_json({"doctypes": doctypes, "before": now()}))
