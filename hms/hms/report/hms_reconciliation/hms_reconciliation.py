import frappe
from frappe.utils import flt

from hms.workflows import BILLING_ROLES, require_roles


def execute(filters=None):
	require_roles(BILLING_ROLES)
	filters = filters or {}
	conditions = {"invoice_type": "Invoice", "status": ["not in", ["Draft", "Void"]]}
	if filters.get("patient"):
		conditions["patient"] = filters["patient"]
	if filters.get("outstanding_only"):
		conditions["outstanding_amount"] = [">", 0]
	columns = [
		{
			"label": "Invoice",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "HMS Invoice",
			"width": 190,
		},
		{"label": "Patient", "fieldname": "patient", "fieldtype": "Link", "options": "Patient", "width": 180},
		{"label": "Payer", "fieldname": "payer_name", "fieldtype": "Data", "width": 180},
		{"label": "Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 110},
		{"label": "Currency", "fieldname": "currency", "fieldtype": "Data", "width": 85},
	] + [
		{"label": label, "fieldname": field, "fieldtype": "Currency", "options": "currency", "width": 125}
		for label, field in [
			("Invoiced", "total"),
			("Credits", "credited_amount"),
			("Net Receipts", "paid_amount"),
			("Outstanding", "outstanding_amount"),
			("Refund Due", "refund_due"),
		]
	]
	rows = frappe.get_list(
		"HMS Invoice",
		filters=conditions,
		fields=[c["fieldname"] for c in columns] + ["status"],
		order_by="invoice_date desc, name desc",
		limit_page_length=0,
	)
	# Never add monetary values of different currencies together.
	currencies = {row.currency for row in rows}
	summary = []
	if len(currencies) == 1:
		currency = next(iter(currencies))
		for label, field in [
			("Outstanding", "outstanding_amount"),
			("Net Receipts", "paid_amount"),
			("Refund Due", "refund_due"),
		]:
			summary.append(
				{
					"label": label,
					"value": flt(sum(row.get(field) or 0 for row in rows), 2),
					"datatype": "Currency",
					"currency": currency,
				}
			)
	return columns, rows, None, None, summary
