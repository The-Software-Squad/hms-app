import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, nowdate

from hms.billing import create_source_invoice, money
from hms.collections import update_collection_status, validate_return
from hms.stock import move
from hms.workflows import PHARMACY_ROLES, atomic_action, immutable, lock, require_roles


def row_values(rows):
	return [
		(r.stock_lot, flt(r.med_quantity), money(r.med_price), r.prescription_row, r.med_name) for r in rows
	]


class MedsOut(Document):
	def validate(self):
		self.currency = self.currency or frappe.db.get_single_value("Hospital Settings", "currency") or "INR"
		old = self.get_doc_before_save()
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_dispensing:
			frappe.throw(_("Use Post Dispensing to change stock."))
		if not frappe.flags.hms_dispensing:
			for field in ("collection_tracking", "collection_status"):
				if str(self.get(field) or "") != str(old.get(field) or "" if old else ""):
					frappe.throw(_("Collection tracking and status are assigned by pharmacy workflows."))
		if self.meds_out_type == "Existing Patient" and not self.patient:
			frappe.throw(_("Select the patient."))
		if self.meds_out_type == "Outside Patient" and not self.customer_name:
			frappe.throw(_("Enter the outside customer's name."))
		if getdate(self.date) > getdate(nowdate()):
			frappe.throw(_("Dispensing date cannot be in the future."))
		if self.transaction_type == "Return" and not self.return_against:
			frappe.throw(_("Select the original dispensing record for a return."))
		if self.transaction_type == "Sale" and self.return_against:
			frappe.throw(_("A sale cannot reference a return source."))
		if len({r.stock_lot for r in self.details}) != len(self.details):
			frappe.throw(_("Use one row per stock lot."))
		self.med_total_amount = 0
		for row in self.details:
			row.med_quantity, row.med_price = flt(row.med_quantity, 6), money(row.med_price)
			if row.med_quantity <= 0 or row.med_price < 0:
				frappe.throw(_("Quantities must be positive and prices non-negative."))
			row.amount = money(row.med_quantity * row.med_price)
			self.med_total_amount += row.amount
		self.med_total_amount = money(self.med_total_amount)
		if old and old.status in ("Posted", "Legacy"):
			immutable(
				self,
				(
					"status",
					"patient",
					"customer_name",
					"meds_out_type",
					"date",
					"transaction_type",
					"return_against",
					"patient_visit",
					"med_total_amount",
					"invoice",
					"currency",
					"posted_by",
					"posted_on",
					"return_origin",
					"return_disposition",
					"return_reason",
					"collection_tracking",
					"collection_status",
				),
			)
			if row_values(self.details) != row_values(old.details):
				frappe.throw(_("Posted dispensing is immutable; record a return instead."))

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def post(self):
		require_roles(PHARMACY_ROLES)
		self.check_permission("write")
		stored = frappe.db.get_value(
			self.doctype, self.name, ["return_against", "patient_visit"], as_dict=True
		)
		if stored.return_against:
			lock(self.doctype, stored.return_against)
		if stored.patient_visit:
			lock("Patient Visit", stored.patient_visit)
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Posted":
			return self.name
		if self.status != "Draft":
			frappe.throw(_("Legacy dispensing is retained for reference and cannot be posted again."))
		self.validate()
		if not self.details:
			frappe.throw(_("Add at least one dispensing row."))
		for lot in sorted(r.stock_lot for r in self.details):
			lock("HMS Stock Lot", lot)
		original = None
		if self.transaction_type == "Return":
			original = frappe.get_doc(self.doctype, self.return_against, for_update=True)
			original.check_permission("read")
			if (
				original.status != "Posted"
				or original.transaction_type != "Sale"
				or original.patient != self.patient
				or original.customer_name != self.customer_name
				or original.currency != self.currency
			):
				frappe.throw(_("The return must match a posted sale for this customer."))
			if not (self.return_reason or "").strip() or self.return_disposition not in (
				"Quarantine",
				"Restock",
			):
				frappe.throw(
					_(
						"Record the return reason and choose quarantine or restock after inspecting the medicines."
					)
				)
			if self.patient_visit != original.patient_visit:
				frappe.throw(_("The return must keep the original prescription reference."))
		prescription = None
		if self.patient_visit:
			prescription = frappe.get_doc("Patient Visit", self.patient_visit, for_update=True)
			prescription.check_permission("read")
			if prescription.patient != self.patient or (
				not original and prescription.status not in ("Prescription Given", "Completed")
			):
				frappe.throw(_("Dispensing must match a saved prescription for the same patient."))
		for row in self.details:
			lot = frappe.get_doc("HMS Stock Lot", row.stock_lot, for_update=True)
			if original:
				original_row = next((r for r in original.details if r.stock_lot == row.stock_lot), None)
				if (
					not original_row
					or money(row.med_price) != money(original_row.med_price)
					or row.prescription_row != original_row.prescription_row
				):
					frappe.throw(_("A return must use the original lot, price and prescription row."))
				returned = frappe.db.sql(
					"""select coalesce(sum(r.med_quantity),0) from `tabOut Medical Item` r
					join `tabMeds Out` m on m.name=r.parent where m.transaction_type='Return' and m.status='Posted'
					and m.return_against=%s and r.stock_lot=%s and r.parenttype='Meds Out' FOR UPDATE""",
					(original.name, lot.name),
				)[0][0]
				if flt(returned + row.med_quantity, 6) > flt(original_row.med_quantity, 6):
					frappe.throw(_("Return quantity exceeds the unreturned original quantity."))
				validate_return(original, row, self.return_origin)
				if self.return_disposition == "Restock" and getdate(lot.expires_at) < getdate(nowdate()):
					frappe.throw(_("Expired returns must remain in quarantine for disposal."))
			else:
				if getdate(lot.expires_at) < getdate(nowdate()) or getdate(lot.expires_at) < getdate(
					self.date
				):
					frappe.throw(_("Expired lots cannot be dispensed."))
				if prescription:
					prescribed = next(
						(r for r in prescription.medication_schedule if r.name == row.prescription_row), None
					)
					if (
						not prescribed
						or frappe.db.get_value("Medicine", prescribed.medicine, "med_item")
						!= lot.medical_item
					):
						frappe.throw(
							_("Select a prescription row whose medicine maps to this pharmacy item.")
						)
					if not prescribed.quantity or prescribed.quantity <= 0:
						frappe.throw(
							_("The doctor must enter an approved dispense quantity on the prescription.")
						)
					dispensed = frappe.db.sql(
						"""select coalesce(sum(case when m.transaction_type='Return' then -r.med_quantity else r.med_quantity end),0)
						from `tabOut Medical Item` r join `tabMeds Out` m on m.name=r.parent
						where m.patient_visit=%s and m.status='Posted' and r.prescription_row=%s and r.parenttype='Meds Out' FOR UPDATE""",
						(prescription.name, prescribed.name),
					)[0][0]
					if flt(dispensed + row.med_quantity, 6) > flt(prescribed.quantity, 6):
						frappe.throw(_("Dispensing exceeds the remaining prescribed quantity."))
			quantity = row.med_quantity if original else -row.med_quantity
			move(
				lot.name,
				quantity,
				f"Dispense:{self.name}:{row.name}",
				self.doctype,
				self.name,
				(self.return_reason if original else "Medicine dispensed"),
				bucket="Quarantine" if original and self.return_disposition == "Quarantine" else "Available",
			)
		payer = (
			frappe.db.get_value("Patient", self.patient, "patient_name")
			if self.patient
			else self.customer_name
		)
		if self.med_total_amount:
			self.invoice = create_source_invoice(
				self.doctype,
				self.name,
				self.patient,
				payer,
				[
					{
						"description": f"Stock lot {r.stock_lot}",
						"quantity": r.med_quantity,
						"rate": r.med_price,
					}
					for r in self.details
				],
				invoice_type="Credit" if original else "Invoice",
				credit_against=original.invoice if original else None,
				currency=self.currency,
			)
		if not original:
			self.collection_tracking, self.collection_status = 1, "Not Collected"
		self.status, self.posted_by, self.posted_on = "Posted", frappe.session.user, now_datetime()
		frappe.flags.hms_dispensing = True
		try:
			self.save()
		finally:
			frappe.flags.hms_dispensing = False
		if original:
			update_collection_status(original)
		return self.name

	@frappe.whitelist()
	def collection_items(self):
		require_roles(PHARMACY_ROLES)
		self.check_permission("read")
		from hms.collections import handed_quantity, returned_quantity

		sale = frappe.get_doc(self.doctype, self.name)
		if sale.status != "Posted" or sale.transaction_type != "Sale" or not sale.collection_tracking:
			frappe.throw(_("Select a posted sale with collection tracking."))
		return [
			{
				"stock_lot": r.stock_lot,
				"quantity": flt(
					r.med_quantity
					- handed_quantity(sale.name, r.stock_lot)
					- returned_quantity(sale.name, r.stock_lot, "Uncollected"),
					6,
				),
			}
			for r in sale.details
			if flt(
				r.med_quantity
				- handed_quantity(sale.name, r.stock_lot)
				- returned_quantity(sale.name, r.stock_lot, "Uncollected"),
				6,
			)
			> 0
		]

	def on_trash(self):
		if self.status in ("Posted", "Legacy"):
			frappe.throw(_("Posted dispensing cannot be deleted; use a return."))
