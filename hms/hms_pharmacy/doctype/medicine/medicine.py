# Copyright (c) 2025, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from hms.workflows import current_rows, lock


class Medicine(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if old and any(
			(self.get(key) or "") != (old.get(key) or "") for key in ("label", "composition", "med_item")
		):
			self._require_unused()

	def before_rename(self, old, new, merge=False):
		self._require_unused()

	def _require_unused(self):
		lock(self.doctype, self.name)
		if current_rows("Medication Schedule", {"medicine": self.name}, ["name"]):
			frappe.throw(
				_(
					"This medicine is used by prescriptions. Create a new medicine and amend the prescription with a correction reason instead of changing its identity or pharmacy item."
				)
			)
