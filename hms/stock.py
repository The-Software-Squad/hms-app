"""Transactional stock movements. All balances are derived from append-only movement records."""
import frappe
from frappe import _
from frappe.utils import flt, now_datetime

from hms.workflows import lock


def move(lot, quantity, event_key, doctype, source, reason, bucket="Available"):
	if bucket not in ("Available", "Quarantine"):
		frappe.throw(_("Select an available or quarantine stock bucket."))
	field = "available_quantity" if bucket == "Available" else "quarantined_quantity"
	lock("HMS Stock Lot", lot)
	if frappe.db.exists("HMS Stock Movement", {"event_key": event_key}):
		return
	quantity = flt(quantity, 6)
	balance = flt(frappe.db.get_value("HMS Stock Lot", lot, field, for_update=True), 6)
	if not quantity or flt(balance + quantity, 6) < 0:
		frappe.throw(_("The movement would make stock negative, or has zero quantity."))
	frappe.flags.hms_stock_posting = True
	try:
		frappe.get_doc(
			{
				"doctype": "HMS Stock Movement",
				"stock_lot": lot,
				"quantity": quantity,
				"stock_bucket": bucket,
				"event_key": event_key,
				"source_doctype": doctype,
				"source_name": source,
				"reason": reason,
				"recorded_by": frappe.session.user,
				"posting_time": now_datetime(),
			}
		).insert(ignore_permissions=True)
	finally:
		frappe.flags.hms_stock_posting = False
	frappe.db.set_value("HMS Stock Lot", lot, field, flt(balance + quantity, 6), update_modified=False)
	row = frappe.db.get_value("HMS Stock Lot", lot, "intake_row")
	if row and bucket == "Available":
		frappe.db.set_value(
			"Intake Medical Item", row, "available_stock", flt(balance + quantity, 6), update_modified=False
		)
