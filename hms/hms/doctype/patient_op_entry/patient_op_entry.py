# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class PatientOPEntry(Document):
    def autoname(self):
        # Get Patient record
        patient = frappe.get_doc('Patient', self.parent)

        # Get the patient's name
        patient_name = patient.patient_name
        self.name = f'OP-{patient_name}-{self.op_date}'

    def validate(self):
        # Set the expires till if not set
        self.op_valid_till = self.op_date + timedelta(days=14)
