# Copyright (c) 2025, HMS
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HealthcarePractitioner(Document):
    def validate(self):
        # Ensure name is consistent with linked employee
        if self.employee and not self.practitioner_name:
            self.practitioner_name = frappe.db.get_value("Employee", self.employee, "employee_name")

