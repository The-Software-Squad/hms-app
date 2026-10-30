import frappe
from frappe import _
from frappe.model.document import Document

from hms.workflows import lock


class Bed(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if (
			self.current_patient
			or self.current_admission
			or (old and (old.current_patient or old.current_admission))
		):
			if not old or any(
				self.get(k) != old.get(k)
				for k in ("current_patient", "current_admission", "ward", "bed_number")
			):
				frappe.throw(_("Occupied beds are managed through admissions and cannot be edited directly."))
		lock("Ward", self.ward)
		capacity = frappe.db.get_value("Ward", self.ward, "capacity")
		if capacity and frappe.db.count("Bed", {"ward": self.ward, "name": ["!=", self.name]}) >= capacity:
			frappe.throw(_("The ward's bed capacity has been reached."))

	def on_trash(self):
		if self.current_patient or self.current_admission:
			frappe.throw(_("An occupied bed cannot be deleted."))
