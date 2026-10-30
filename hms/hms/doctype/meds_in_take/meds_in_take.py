import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, nowdate

from hms.billing import money
from hms.stock import move
from hms.workflows import PHARMACY_ROLES, atomic_action, immutable, lock, require_roles


def row_values(rows):
	return [
		(
			r.name,
			r.medical_item_name,
			r.batch_number,
			str(r.expires_at),
			flt(r.count),
			money(r.single_item_price),
		)
		for r in rows
	]


class MedsIntake(Document):
	def validate(self):
		self.currency = self.currency or frappe.db.get_single_value("Hospital Settings", "currency") or "INR"
		old = self.get_doc_before_save()
		if old and old.status == "Legacy":
			immutable(
				self,
				(
					"status",
					"provider",
					"in_take_date",
					"invoice_number",
					"price",
					"discount",
					"total",
					"currency",
				),
			)
			if row_values(self.table_xxjy) != row_values(old.table_xxjy):
				frappe.throw(
					_("Legacy intake is read-only; verify opening balances in a new intake document.")
				)
			return
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_intake_posting:
			frappe.throw(_("Use the posting or cancellation action."))
		if getdate(self.in_take_date) > getdate(nowdate()):
			frappe.throw(_("Intake date cannot be in the future."))
		self.price = 0
		for row in self.table_xxjy:
			row.count, row.single_item_price = flt(row.count, 6), money(row.single_item_price)
			if row.count <= 0 or row.single_item_price < 0 or not row.batch_number:
				frappe.throw(
					_("Every intake row requires a batch, positive quantity and non-negative unit rate.")
				)
			if not row.expires_at or getdate(row.expires_at) < getdate(self.in_take_date):
				frappe.throw(_("Stock expiry cannot be before its intake date."))
			row.in_take_at, row.intake_provider, row.invoice_number = (
				self.in_take_date,
				self.provider,
				self.invoice_number,
			)
			row.available_stock = (
				flt(frappe.db.get_value("HMS Stock Lot", row.stock_lot, "available_quantity"), 6)
				if row.stock_lot
				else 0
			)
			self.price += money(row.count * row.single_item_price)
		self.price, self.discount = money(self.price), money(self.discount)
		if self.discount < 0 or self.discount > self.price:
			frappe.throw(_("Discount must be between zero and the intake value."))
		self.total = money(self.price - self.discount)
		if old and old.status in ("Posted", "Cancelled"):
			immutable(
				self, ("provider", "in_take_date", "invoice_number", "price", "discount", "total", "currency")
			)
			if row_values(self.table_xxjy) != row_values(old.table_xxjy):
				frappe.throw(_("Posted intake rows are immutable; cancel or adjust stock."))

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
		if self.status != "Draft" or not self.table_xxjy:
			frappe.throw(_("Only an intake draft with items can be posted."))
		self.validate()
		for row in self.table_xxjy:
			if getdate(row.expires_at) < getdate(nowdate()):
				frappe.throw(_("Expired stock cannot be posted as available inventory."))
			frappe.flags.hms_stock_posting = True
			try:
				lot = frappe.get_doc(
					{
						"doctype": "HMS Stock Lot",
						"medical_item": row.medical_item_name,
						"intake": self.name,
						"intake_row": row.name,
						"batch_number": row.batch_number,
						"expires_at": row.expires_at,
						"unit_rate": row.single_item_price,
						"currency": self.currency,
						"available_quantity": 0,
					}
				).insert(ignore_permissions=True)
			finally:
				frappe.flags.hms_stock_posting = False
			move(
				lot.name,
				row.count,
				f"Intake:{self.name}:{row.name}",
				self.doctype,
				self.name,
				"Stock received",
			)
			row.stock_lot = lot.name
		self.status, self.posted_by, self.posted_on = "Posted", frappe.session.user, now_datetime()
		frappe.flags.hms_intake_posting = True
		try:
			self.save()
		finally:
			frappe.flags.hms_intake_posting = False
		return self.name

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def cancel_intake(self, reason):
		require_roles(PHARMACY_ROLES)
		self.check_permission("write")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Cancelled":
			return self.name
		if self.status != "Posted" or not reason or not reason.strip():
			frappe.throw(_("A posted intake and cancellation reason are required."))
		for row in sorted(self.table_xxjy, key=lambda r: r.stock_lot):
			move(
				row.stock_lot,
				-row.count,
				f"CancelIntake:{self.name}:{row.name}",
				self.doctype,
				self.name,
				reason.strip(),
			)
		self.status = "Cancelled"
		frappe.flags.hms_intake_posting = True
		try:
			self.save()
		finally:
			frappe.flags.hms_intake_posting = False
		return self.name

	def on_trash(self):
		if self.status != "Draft":
			frappe.throw(_("Posted intake history cannot be deleted."))
