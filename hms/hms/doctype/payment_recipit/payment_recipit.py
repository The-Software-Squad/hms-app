import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

from hms.billing import money, recalculate_invoice
from hms.workflows import BILLING_ROLES, atomic_action, immutable, lock, require_roles


class PaymentRecipit(Document):
	def validate(self):
		self.currency = self.currency or frappe.db.get_single_value("Hospital Settings", "currency") or "INR"
		if not self.patient and not self.paid_by:
			frappe.throw(_("Select a patient or enter Paid By."))
		if self.patient and not self.paid_by:
			self.paid_by = frappe.db.get_value("Patient", self.patient, "patient_name")
		if money(self.amount) <= 0:
			frappe.throw(_("Payment amount must be positive."))
		if getdate(self.payment_date) > getdate(nowdate()):
			frappe.throw(_("Payment date cannot be in the future."))
		if self.transaction_type == "Refund" and not self.reference_receipt:
			frappe.throw(_("A refund must reference its original receipt."))
		for allocation in self.allocations:
			allocation.amount = money(allocation.amount)
		old = self.get_doc_before_save()
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_payment_posting:
			frappe.throw(_("Use Post Payment to change payment state."))
		if old and old.status == "Legacy Recorded":
			immutable(
				self,
				(
					"patient",
					"paid_by",
					"payment_date",
					"amount",
					"towards",
					"payment_mode",
					"reference_number",
					"transaction_type",
					"reference_receipt",
					"currency",
				),
			)
		if old and old.status == "Posted":
			immutable(
				self,
				(
					"status",
					"patient",
					"paid_by",
					"payment_date",
					"amount",
					"towards",
					"payment_mode",
					"reference_number",
					"payment_category",
					"currency",
					"transaction_type",
					"reference_receipt",
					"posted_by",
					"posted_on",
				),
			)
			if [(r.invoice, money(r.amount)) for r in self.allocations] != [
				(r.invoice, money(r.amount)) for r in old.allocations
			]:
				frappe.throw(_("Posted allocations cannot be edited; use a refund."))

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def post(self):
		require_roles(BILLING_ROLES)
		self.check_permission("write")
		# Original receipt first, then own row, then sorted invoice locks: stable refund lock order.
		stored = frappe.db.get_value(
			self.doctype, self.name, ["transaction_type", "reference_receipt"], as_dict=True
		)
		if stored.transaction_type == "Refund":
			lock(self.doctype, stored.reference_receipt)
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.status == "Posted":
			return self.name
		self.validate()
		if not self.allocations or money(sum(r.amount for r in self.allocations)) != money(self.amount):
			frappe.throw(_("Allocate the full payment amount to invoices before posting."))
		if len({r.invoice for r in self.allocations}) != len(self.allocations):
			frappe.throw(_("Use one allocation row per invoice."))
		original = None
		if self.transaction_type == "Refund":
			original = frappe.get_doc(self.doctype, self.reference_receipt, for_update=True)
			original.check_permission("read")
			if (
				original.status != "Posted"
				or original.transaction_type != "Receive"
				or original.patient != self.patient
				or original.currency != self.currency
			):
				frappe.throw(_("Refund must reference a posted receipt for the same patient."))
		for name in sorted(r.invoice for r in self.allocations):
			lock("HMS Invoice", name)
		for row in self.allocations:
			invoice = frappe.get_doc("HMS Invoice", row.invoice, for_update=True)
			invoice.check_permission("read")
			if (
				invoice.patient != self.patient
				or invoice.invoice_type != "Invoice"
				or invoice.status in ("Draft", "Void")
				or invoice.currency != self.currency
			):
				frappe.throw(
					_("Allocations must reference issued invoices for the same patient and currency.")
				)
			recalculate_invoice(invoice.name)
			invoice.reload()
			if money(row.amount) <= 0:
				frappe.throw(_("Allocation amounts must be positive."))
			if not original and money(row.amount) > money(invoice.outstanding_amount):
				frappe.throw(_("Payment exceeds the invoice outstanding amount."))
			if original:
				original_amount = sum(r.amount for r in original.allocations if r.invoice == row.invoice)
				refunded = frappe.db.sql(
					"""select coalesce(sum(a.amount),0) from `tabHMS Payment Allocation` a
					join `tabPayment Recipit` p on p.name=a.parent where p.status='Posted' and p.transaction_type='Refund'
					and p.reference_receipt=%s and a.invoice=%s and a.parenttype='Payment Recipit' FOR UPDATE""",
					(original.name, row.invoice),
				)[0][0]
				if money(row.amount + refunded) > money(original_amount) or money(row.amount) > money(
					invoice.paid_amount
				):
					frappe.throw(_("Refund exceeds the unrefunded original allocation."))
		frappe.flags.hms_payment_posting = True
		try:
			self.status, self.posted_by, self.posted_on = "Posted", frappe.session.user, now_datetime()
			self.save()
		finally:
			frappe.flags.hms_payment_posting = False
		for row in self.allocations:
			recalculate_invoice(row.invoice)
		return self.name

	def on_trash(self):
		if self.status in ("Posted", "Legacy Recorded"):
			frappe.throw(_("Posted receipts cannot be deleted; issue a refund instead."))
