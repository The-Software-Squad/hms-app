# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class Patient(Document):
    def validate(self):
        latest_expires_on = None

        # Iterate through child records to find the latest op_expires_on date
        for op_record in self.get('patient_op_list'):
            if op_record.op_valid_from:
                # Convert the string date to a datetime object
                valid_from_date = datetime.strptime(op_record.op_valid_from, '%Y-%m-%d').date()
                # Calculate the expiry date
                expires_on_date = valid_from_date + timedelta(days=14)
                op_record.op_expires_on = expires_on_date.strftime('%Y-%m-%d')

                # Compare and update latest_expires_on
                expires_on_date_obj = datetime.strptime(op_record.op_expires_on, '%Y-%m-%d').date()
                if latest_expires_on is None or expires_on_date_obj > latest_expires_on:
                    latest_expires_on = expires_on_date_obj

        # Set the latest op_expires_on date as a property on the parent document
        if latest_expires_on:
            self.latest_op_expires_on = latest_expires_on.strftime('%Y-%m-%d')
