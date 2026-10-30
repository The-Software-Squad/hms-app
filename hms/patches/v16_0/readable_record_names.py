"""Replace public hash IDs without changing balances or losing source/idempotency links."""

import re

import frappe
from frappe.model.naming import getseries, make_autoname
from frappe.model.rename_doc import rename_doc
from frappe.utils import get_datetime

PUBLIC_PREFIXES = {
	"Meds In take": "HMS-INT-",
	"Meds Out": "HMS-DSP-",
	"HMS Medication Delivery": "HMS-MDL-",
	"HMS Patient Merge": "HMS-MRG-",
	"HMS Stock Adjustment": "HMS-ADJ-",
	"HMS Stock Movement": "HMS-MOV-",
}


def reserve_existing_sequences():
	# Previously, brace-style format counters shared the empty-prefix Series row.
	for doctype, pattern in (
		("Employee", r"(EMP-)(\d+)"),
		("HMS Invoice", r"(HMS-INV-\d{4}-)(\d+)"),
		("HMS Stock Lot", r"(HMS-LOT-)(\d+)"),
	):
		maximums = {}
		for name in frappe.get_all(doctype, pluck="name"):
			if match := re.fullmatch(pattern, name):
				prefix, number = match.groups()
				maximums[prefix] = max(maximums.get(prefix, 0), int(number))
		for prefix, maximum in maximums.items():
			# Create/lock the counter through Frappe before advancing it.
			current = int(getseries(prefix, 1)) - 1
			series = frappe.qb.DocType("Series")
			frappe.qb.update(series).set(series.current, max(current, maximum)).where(
				series.name == prefix
			).run()


def update_source_keys(doctype, old, new):
	for name in frappe.get_all("HMS Invoice", filters={"source_key": f"{doctype}:{old}"}, pluck="name"):
		frappe.db.set_value(
			"HMS Invoice", name, {"source_key": f"{doctype}:{new}", "source_name": new}, update_modified=False
		)
	for row in frappe.get_all(
		"HMS Stock Movement", filters={"source_doctype": doctype}, fields=["name", "source_name", "event_key"]
	):
		parts = (row.event_key or "").split(":")
		if len(parts) > 1 and parts[1] == old:
			parts[1] = new
			frappe.db.set_value(
				"HMS Stock Movement",
				row.name,
				{"source_name": new, "event_key": ":".join(parts)},
				update_modified=False,
			)


def execute():
	reserve_existing_sequences()
	for doctype, prefix in PUBLIC_PREFIXES.items():
		for record in frappe.get_all(doctype, fields=["name", "creation"], order_by="creation, name"):
			if not re.fullmatch(r"[a-z0-9]{10}", record.name):
				continue
			year = get_datetime(record.creation).year
			new = make_autoname(f"{prefix}{year}-.#####")
			while frappe.db.exists(doctype, new):
				new = make_autoname(f"{prefix}{year}-.#####")
			rename_doc(
				doctype,
				record.name,
				new,
				force=True,
				ignore_permissions=True,
				show_alert=False,
				rebuild_search=False,
			)
			frappe.db.set_value(doctype, new, "legacy_id", record.name, update_modified=False)
			update_source_keys(doctype, record.name, new)
	frappe.clear_cache()
