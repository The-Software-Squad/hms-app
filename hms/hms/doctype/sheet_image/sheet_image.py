# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SheetImage(Document):
    def autoname(self):
            # Check if self.parent refers directly to a Patient record
            if self.parent and self.parenttype == "Patient":
                # Get Patient record
                patient = frappe.get_doc('Patient', self.parent)

                # Get the patient's name
                patient_name = patient.patient_name

                # Generate a unique identifier
                unique_id = frappe.generate_hash(length=8)

                # Set the name for SheetImage
                self.name = f"OP-{patient_name}-{unique_id}"
            else:
                # Handle the case where parent is not a Patient record
                frappe.throw(f"Parent document must be a Patient record")
