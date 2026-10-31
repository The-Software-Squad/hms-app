import frappe
from frappe import _
from frappe.model.document import Document


class HMSStockMovement(Document):
	def validate(self):
		if not self.is_new() or not frappe.flags.hms_stock_posting:
			frappe.throw(_("Stock movements are append-only records created by posting a source document."))

	def on_trash(self):
		frappe.throw(_("Stock movements cannot be deleted; post a reversing movement."))
