import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class Ward(Document):
	def validate(self):
		if cint(self.capacity) < 1:
			frappe.throw(_("Ward capacity must be positive."))
		beds = frappe.db.count("Bed", {"ward": self.name}) if not self.is_new() else 0
		if cint(self.capacity) < beds:
			frappe.throw(_("Capacity cannot be less than the existing number of beds."))
		self.total_occupied = (
			frappe.db.count("Bed", {"ward": self.name, "current_patient": ["is", "set"]})
			if not self.is_new()
			else 0
		)
