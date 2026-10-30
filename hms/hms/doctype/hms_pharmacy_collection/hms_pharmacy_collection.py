import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, getdate, now_datetime

from hms.collections import handed_quantity, returned_quantity, update_collection_status
from hms.workflows import PHARMACY_ROLES, atomic_action, immutable, lock, require_roles


class HMSPharmacyCollection(Document):
	def validate(self):
		old = self.get_doc_before_save()
		immutable(self, ("source_sale",))
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_collection:
			frappe.throw(_("Use Post Handover."))
		if not frappe.flags.hms_collection:
			for field in ("handed_by", "posted_on"):
				if str(self.get(field) or "") != str(old.get(field) or "" if old else ""):
					frappe.throw(_("Handover audit fields are assigned when posted."))
		if not (self.recipient_name or "").strip() or not self.details:
			frappe.throw(_("Enter the recipient's name and the medicines actually handed over."))
		if len({r.stock_lot for r in self.details}) != len(self.details) or any(
			flt(r.quantity, 6) <= 0 for r in self.details
		):
			frappe.throw(_("Use one row per lot and positive handover quantities."))
		if old and old.status == "Posted":
			immutable(
				self, ("source_sale", "collected_on", "recipient_name", "status", "handed_by", "posted_on")
			)
			if [(r.stock_lot, flt(r.quantity, 6)) for r in self.details] != [
				(r.stock_lot, flt(r.quantity, 6)) for r in old.details
			]:
				frappe.throw(
					_(
						"Posted handovers are retained unchanged. Record a medicine return to reverse a collection."
					)
				)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def post(self):
		require_roles(PHARMACY_ROLES)
		self.check_permission("write")
		source = frappe.db.get_value(self.doctype, self.name, "source_sale")
		lock("Meds Out", source)
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Posted":
			return self.name
		self.validate()
		sale = frappe.get_doc("Meds Out", self.source_sale, for_update=True)
		sale.check_permission("read")
		if sale.status != "Posted" or sale.transaction_type != "Sale" or not sale.collection_tracking:
			frappe.throw(_("Collection requires a posted sale with collection tracking enabled."))
		if get_datetime(self.collected_on) > now_datetime() or getdate(self.collected_on) < getdate(
			sale.date
		):
			frappe.throw(_("Handover must be between the dispensing date and now."))
		for row in sorted(self.details, key=lambda r: r.stock_lot):
			lock("HMS Stock Lot", row.stock_lot)
			original = next((r for r in sale.details if r.stock_lot == row.stock_lot), None)
			if not original:
				frappe.throw(_("Only lots on the original dispensing record can be handed over."))
			if getdate(frappe.db.get_value("HMS Stock Lot", row.stock_lot, "expires_at")) < getdate():
				frappe.throw(
					_("Expired medicines cannot be handed over. Reverse the uncollected dispensing.")
				)
			remaining = (
				flt(original.med_quantity)
				- handed_quantity(sale.name, row.stock_lot)
				- returned_quantity(sale.name, row.stock_lot, "Uncollected")
			)
			if flt(row.quantity, 6) > flt(remaining, 6):
				frappe.throw(_("Handover exceeds the remaining uncollected quantity."))
		self.status, self.handed_by, self.posted_on = "Posted", frappe.session.user, now_datetime()
		frappe.flags.hms_collection = True
		try:
			self.save()
		finally:
			frappe.flags.hms_collection = False
		update_collection_status(sale)
		return self.name

	def on_trash(self):
		if self.status == "Posted":
			frappe.throw(_("Posted handovers must retain their history."))
