import frappe
from frappe import _
from frappe.model.document import Document


class HMSStockLot(Document):
	def validate(self):
		if not frappe.flags.hms_stock_posting:
			frappe.throw(
				_("Stock lots are created by posted intake; use stock adjustments to change quantities.")
			)

	def on_trash(self):
		frappe.throw(_("Stock lots must retain their movement history."))
