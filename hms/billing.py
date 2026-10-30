"""Standalone operational invoices, allocations and reversals. No ERPNext or payment gateway required."""
import frappe
from frappe import _
from frappe.utils import flt, now_datetime, nowdate

from hms.workflows import lock


def money(value):
	return flt(value, 2)


def recalculate_invoice(name):
	invoice = frappe.db.get_value(
		"HMS Invoice", name, ["total", "status", "invoice_type"], as_dict=True, for_update=True
	)
	if not invoice or invoice.status in ("Draft", "Void") or invoice.invoice_type == "Credit":
		return
	credits = money(
		frappe.db.sql(
			"""select coalesce(sum(total),0) from `tabHMS Invoice`
		where credit_against=%s and invoice_type='Credit' and status not in ('Draft','Void') FOR UPDATE""",
			(name,),
		)[0][0]
	)
	paid = money(
		frappe.db.sql(
			"""select coalesce(sum(case when p.transaction_type='Refund' then -a.amount else a.amount end),0)
		from `tabHMS Payment Allocation` a join `tabPayment Recipit` p on p.name=a.parent
		where a.parenttype='Payment Recipit' and a.parentfield='allocations' and a.invoice=%s and p.status='Posted' FOR UPDATE""",
			(name,),
		)[0][0]
	)
	due = money(max(0, invoice.total - credits - paid))
	refund = money(max(0, paid - (invoice.total - credits)))
	status = "Refund Due" if refund else ("Paid" if not due else ("Partly Paid" if paid else "Issued"))
	frappe.db.set_value(
		"HMS Invoice",
		name,
		{
			"credited_amount": credits,
			"paid_amount": paid,
			"outstanding_amount": due,
			"refund_due": refund,
			"status": status,
		},
		update_modified=False,
	)


def issue_invoice(invoice):
	if invoice.status != "Draft":
		return invoice.name
	if invoice.invoice_type == "Credit":
		lock("HMS Invoice", invoice.credit_against)
		original = frappe.get_doc("HMS Invoice", invoice.credit_against, for_update=True)
		if original.invoice_type != "Invoice" or original.status in ("Draft", "Void"):
			frappe.throw(_("A credit must reference an issued invoice."))
		if original.patient != invoice.patient or original.currency != invoice.currency:
			frappe.throw(_("Credit patient and currency must match the original invoice."))
		recalculate_invoice(original.name)
		credited = frappe.db.get_value("HMS Invoice", original.name, "credited_amount") or 0
		if money(credited + invoice.total) > money(original.total):
			frappe.throw(_("Credit exceeds the remaining invoice amount."))
	frappe.flags.hms_invoice_service = True
	try:
		invoice.status = "Issued"
		invoice.issued_by, invoice.issued_on = frappe.session.user, now_datetime()
		invoice.save(ignore_permissions=True)
	finally:
		frappe.flags.hms_invoice_service = False
	recalculate_invoice(invoice.credit_against if invoice.invoice_type == "Credit" else invoice.name)
	return invoice.name


def create_source_invoice(
	doctype, name, patient, payer, items, invoice_type="Invoice", credit_against=None, currency=None
):
	key = f"{doctype}:{name}"
	existing = frappe.db.get_value("HMS Invoice", {"source_key": key}, "name")
	if existing:
		return existing
	currency = (
		currency
		or (frappe.db.get_value("HMS Invoice", credit_against, "currency") if credit_against else None)
		or frappe.db.get_single_value("Hospital Settings", "currency")
		or "INR"
	)
	frappe.flags.hms_invoice_service = True
	try:
		invoice = frappe.get_doc(
			{
				"doctype": "HMS Invoice",
				"patient": patient,
				"payer_name": payer,
				"source_key": key,
				"source_doctype": doctype,
				"source_name": name,
				"invoice_date": nowdate(),
				"currency": currency,
				"invoice_type": invoice_type,
				"credit_against": credit_against,
				"items": items,
				"status": "Draft",
			}
		).insert(ignore_permissions=True)
	finally:
		frappe.flags.hms_invoice_service = False
	issue_invoice(invoice)
	return invoice.name


def ensure_visit_invoice(visit):
	rate = frappe.db.get_value("Department Type", visit.department, "out_patient_fees")
	if rate is None or rate == 0:
		rate = frappe.db.get_single_value("Hospital Settings", "fee_validity_rate") or 0
	if money(rate) <= 0:
		return
	patient_name = frappe.db.get_value("Patient", visit.patient, "patient_name")
	invoice = create_source_invoice(
		visit.doctype,
		visit.name,
		visit.patient,
		patient_name,
		[{"description": f"Consultation: {visit.name}", "quantity": 1, "rate": rate}],
	)
	visit.db_set("invoice", invoice, update_modified=False)


def validate_source_invoice_cancellation(doctype, name):
	invoice_name = frappe.db.get_value("HMS Invoice", {"source_key": f"{doctype}:{name}"}, "name")
	if not invoice_name:
		return
	lock("HMS Invoice", invoice_name)
	invoice = frappe.get_doc("HMS Invoice", invoice_name, for_update=True)
	if invoice.status == "Void":
		return
	recalculate_invoice(invoice_name)
	invoice = frappe.get_doc("HMS Invoice", invoice_name, for_update=True)
	if money(invoice.paid_amount):
		frappe.throw(_("Refund the linked payment before cancelling this consultation charge."))
	if money(invoice.credited_amount):
		if money(invoice.credited_amount) == money(invoice.total) and not money(invoice.outstanding_amount):
			# Clinical closure must retain the issued invoice and its full credit/refund history.
			return invoice
		frappe.throw(_("Credit the remaining consultation charge before cancelling this visit."))
	return invoice


def void_source_invoice(doctype, name, reason):
	invoice = validate_source_invoice_cancellation(doctype, name)
	if not invoice:
		return
	if money(invoice.credited_amount):
		return invoice.name
	invoice.db_set({"status": "Void", "void_reason": reason}, update_modified=False)
