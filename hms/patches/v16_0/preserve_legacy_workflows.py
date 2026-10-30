"""Preserve historical documents without inventing stock movements or payment allocations."""
import frappe

from hms.patches.v16_0.capture_legacy_workflows import KEY


def execute():
	snapshot = frappe.db.get_default(KEY)
	if not snapshot:
		return
	data = frappe.parse_json(snapshot)
	for doctype in data["doctypes"]:
		if doctype not in ("Meds In take", "Meds Out", "Payment Recipit"):
			continue
		status = "Legacy Recorded" if doctype == "Payment Recipit" else "Legacy"
		# Table names come only from the fixed allowlist; values are bound parameters.
		frappe.db.sql(
			f"UPDATE `tab{doctype}` SET status=%s WHERE status='Draft' AND creation<=%s",
			(status, data["before"]),
		)
	frappe.db.set_default(KEY, None)
