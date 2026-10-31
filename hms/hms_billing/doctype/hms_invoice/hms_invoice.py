import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from hms.billing import issue_invoice, money, recalculate_invoice
from hms.workflows import BILLING_ROLES, atomic_action, immutable, lock, require_roles


class HMSInvoice(Document):
	def validate(self):
		old = self.get_doc_before_save()
		immutable(self, ("source_key", "source_doctype", "source_name"))
		if self.is_new() and self.source_key and not frappe.flags.hms_invoice_service:
			frappe.throw(_("Source-linked invoices are created by the source workflow."))
		if self.status != (old.status if old else "Draft") and not frappe.flags.hms_invoice_service:
			frappe.throw(_("Use Issue Invoice or Void Invoice to change invoice state."))
		if getdate(self.invoice_date) > getdate(nowdate()):
			frappe.throw(_("Invoice date cannot be in the future."))
		if self.invoice_type == "Credit" and not self.credit_against:
			frappe.throw(_("Select the invoice being credited."))
		if not self.items:
			frappe.throw(_("Add at least one invoice item."))
		self.total = 0
		for row in self.items:
			if row.quantity <= 0 or row.rate < 0:
				frappe.throw(_("Invoice quantities must be positive and rates non-negative."))
			row.amount = money(row.quantity * row.rate)
			self.total += row.amount
		self.total = money(self.total)
		if old and old.status != "Draft":
			immutable(
				self,
				(
					"patient",
					"payer_name",
					"currency",
					"invoice_date",
					"invoice_type",
					"credit_against",
					"total",
					"issued_by",
					"issued_on",
					"credited_amount",
					"paid_amount",
					"outstanding_amount",
					"refund_due",
				),
			)
			if [(r.description, r.quantity, r.rate) for r in self.items] != [
				(r.description, r.quantity, r.rate) for r in old.items
			]:
				frappe.throw(_("Issued invoice items are immutable; issue a credit instead."))

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def issue(self):
		require_roles(BILLING_ROLES)
		self.check_permission("write")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		return issue_invoice(self)

	@frappe.whitelist(methods=["POST"])
	@atomic_action
	def void(self, reason):
		require_roles(BILLING_ROLES)
		self.check_permission("write")
		lock(self.doctype, self.name)
		self.flags.for_update = True
		self.reload()
		if self.source_key:
			frappe.throw(_("Cancel or return the source record rather than voiding its invoice directly."))
		if not reason or not reason.strip():
			frappe.throw(_("A void reason is required."))
		recalculate_invoice(self.name)
		self.flags.for_update = True
		self.reload()
		if self.paid_amount or self.credited_amount or self.invoice_type == "Credit":
			frappe.throw(_("Paid or credited invoices require a reversal/credit workflow."))
		self.db_set({"status": "Void", "void_reason": reason.strip()})
		return self.name

	def on_trash(self):
		if self.status != "Draft":
			frappe.throw(_("Issued invoices are retained; void or credit them instead."))
