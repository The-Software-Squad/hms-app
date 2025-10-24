# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import getdate

class Patient(Document):
	# def before_save(self):
	#     self.check_op_date_overlap_and_update_latest_expiry_date()

	def validate(self):
		self.check_op_date_overlap_and_update_latest_expiry_date()

	def check_op_date_overlap_and_update_latest_expiry_date(self):
		date_ranges = []
		latest_expiry_date = None

		patient_op_list = self.get('op_records')
		if not patient_op_list:
			return

		# Loop through all the OP entries
		for op_entry in patient_op_list:
			# Get the start and end date of the OP entry
			start_date = getdate(op_entry.get('from'))
			end_date = getdate(op_entry.get('to')) if op_entry.get('to') else start_date + timedelta(days=30)

			# Assign the end date to the OP entry if it was not already set
			if not op_entry.get('to'):
				op_entry.to = end_date

			# Check if the end date is the latest expiry date
			if latest_expiry_date is None or end_date > latest_expiry_date:
				latest_expiry_date = end_date

			# Check if the OP dates overlap with any existing OP dates
			for existing_start, existing_end in date_ranges:
				if start_date <= existing_end and end_date >= existing_start:
					frappe.db.rollback()
					frappe.throw('Overlapping OP dates are not allowed')

			# Add the OP dates to the list
			date_ranges.append((start_date, end_date))

		# Set the latest expiry date; no explicit save in validate
		if latest_expiry_date:
			self.latest_op_expires_on = latest_expiry_date
