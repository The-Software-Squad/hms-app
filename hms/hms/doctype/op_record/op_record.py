# Copyright (c) 2025, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OPRecord(Document):
	def validate(self):
		# Set the expires till if not set
		if not self.valid_till:
			self.valid_till = frappe.utils.add_days(self.start_date, 30)