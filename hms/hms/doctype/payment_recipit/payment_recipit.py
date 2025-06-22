# Copyright (c) 2025, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PaymentRecipit(Document):
	def before_save(self):
		# Check if the paid_by field is empty
		if not self.paid_by and self.patient:
			# Get the patient's name from the patient field
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name")
			if patient_name:
				# Set the paid_by field to the patient's name
				self.paid_by = patient_name
	def validate(self):
		# Conditionally enforce 'paid_by' if 'patient' is not set
		if not self.patient and not self.paid_by:
			frappe.throw("Please enter either <b>Paid By</b> or select the patient <b>Patient</b>.")
