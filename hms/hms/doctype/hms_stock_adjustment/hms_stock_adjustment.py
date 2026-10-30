import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime

from hms.stock import move
from hms.workflows import PHARMACY_ROLES, atomic_action, immutable, lock, require_roles


class HMSStockAdjustment(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if not flt(self.quantity) or not (self.reason or "").strip():
			frappe.throw(_("A nonzero adjustment quantity and reason are required."))
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_adjustment_posting:
			frappe.throw(_("Use Post Adjustment."))
		if old and old.status == "Posted":
			immutable(
				self,
				("stock_lot", "quantity", "reason", "status", "posted_by", "posted_on", "adjustment_type"),
			)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def post(self):
		require_roles(PHARMACY_ROLES)
		self.check_permission("write")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Posted":
			return self.name
		self.validate()
		if self.adjustment_type in ("Release Quarantine", "Dispose Quarantine"):
			if flt(self.quantity) <= 0:
				frappe.throw(_("Enter a positive quantity to release or dispose from quarantine."))
			if (
				self.adjustment_type == "Release Quarantine"
				and getdate(frappe.db.get_value("HMS Stock Lot", self.stock_lot, "expires_at")) < getdate()
			):
				frappe.throw(_("Expired medicines cannot be released from quarantine."))
			move(
				self.stock_lot,
				-self.quantity,
				f"Adjustment:{self.name}:Quarantine",
				self.doctype,
				self.name,
				self.reason,
				bucket="Quarantine",
			)
			if self.adjustment_type == "Release Quarantine":
				move(
					self.stock_lot,
					self.quantity,
					f"Adjustment:{self.name}",
					self.doctype,
					self.name,
					self.reason,
				)
		else:
			move(
				self.stock_lot, self.quantity, f"Adjustment:{self.name}", self.doctype, self.name, self.reason
			)
		self.status, self.posted_by, self.posted_on = "Posted", frappe.session.user, now_datetime()
		frappe.flags.hms_adjustment_posting = True
		try:
			self.save()
		finally:
			frappe.flags.hms_adjustment_posting = False
		return self.name

	def on_trash(self):
		if self.status == "Posted":
			frappe.throw(_("Post a reversing adjustment instead of deleting history."))
