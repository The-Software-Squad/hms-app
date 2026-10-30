"""Physical handovers are distinct from posted dispensing and stock returns."""
import frappe
from frappe import _
from frappe.utils import flt


def handed_quantity(sale, lot):
	return flt(
		frappe.db.sql(
			"""select coalesce(sum(i.quantity),0) from `tabHMS Pharmacy Collection Item` i
		join `tabHMS Pharmacy Collection` c on c.name=i.parent
		where c.source_sale=%s and c.status='Posted' and i.stock_lot=%s
		and i.parenttype='HMS Pharmacy Collection' FOR UPDATE""",
			(sale, lot),
		)[0][0],
		6,
	)


def returned_quantity(sale, lot, origin=None):
	condition = " and m.return_origin=%s" if origin else ""
	args = [sale, lot] + ([origin] if origin else [])
	return flt(
		frappe.db.sql(
			"""select coalesce(sum(i.med_quantity),0) from `tabOut Medical Item` i
		join `tabMeds Out` m on m.name=i.parent where m.return_against=%s and i.stock_lot=%s
		and m.transaction_type='Return' and m.status='Posted' and i.parenttype='Meds Out'"""
			+ condition
			+ " FOR UPDATE",
			args,
		)[0][0],
		6,
	)


def validate_return(sale, row, origin):
	if sale.collection_tracking:
		if origin not in ("Uncollected", "Collected"):
			frappe.throw(_("Choose whether these medicines were collected or remained at the pharmacy."))
		handed = handed_quantity(sale.name, row.stock_lot)
		original = next(r for r in sale.details if r.stock_lot == row.stock_lot)
		capacity = handed if origin == "Collected" else flt(original.med_quantity) - handed
	else:
		if origin != "Legacy Not Tracked":
			frappe.throw(
				_(
					"This historical sale has no collection history. Select Legacy Not Tracked and document the return."
				)
			)
		capacity = next(r.med_quantity for r in sale.details if r.stock_lot == row.stock_lot)
	if flt(returned_quantity(sale.name, row.stock_lot, origin) + row.med_quantity, 6) > flt(capacity, 6):
		frappe.throw(_("The return exceeds the quantity available for the selected collection origin."))


def update_collection_status(sale):
	if not sale.collection_tracking:
		status = "Not Tracked"
	else:
		quantity = sum(flt(r.med_quantity) for r in sale.details)
		returned = sum(returned_quantity(sale.name, r.stock_lot) for r in sale.details)
		handed = sum(handed_quantity(sale.name, r.stock_lot) for r in sale.details)
		uncollected = sum(returned_quantity(sale.name, r.stock_lot, "Uncollected") for r in sale.details)
		status = (
			"Returned"
			if flt(quantity - returned, 6) == 0
			else (
				"Collected"
				if flt(handed + uncollected, 6) >= flt(quantity, 6)
				else ("Partly Collected" if handed else "Not Collected")
			)
		)
	frappe.db.set_value("Meds Out", sale.name, "collection_status", status, update_modified=False)
	return status
