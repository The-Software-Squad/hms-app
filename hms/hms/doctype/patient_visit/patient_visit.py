# Copyright (c) 2025, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime
from hms.utils import has_active_out_patient_record

class PatientVisit(Document):
	def before_insert(self):
		if not self.patient:
			frappe.throw(_("Please select a patient for creating a patient visit"), title="Patient Required")
		
		# check if the patient has an active Out Patient record (child table entry)
		if not has_active_out_patient_record(self.patient):
			frappe.throw(_("Patient does not have an active Out Patient record. Please add one before proceeding."), title="No Active Out Patient")
		

		
	# def validate(self):
	# 	if self.is_new():
	# 		if not self.op_record:
	# 			op = frappe.get_all(
	# 				"OP Record",
	# 				filters={
	# 					"patient": self.patient,
	# 					"status": "Open",
	# 					"valid_till": [">=", frappe.utils.nowdate()]
	# 				},
	# 				fields=["name"],
	# 				limit=1,
	# 				order_by="valid_till desc"
	# 			)

	# 			if op:
	# 				self.op_record = op[0].name
	# 			else:
	# 				frappe.throw(_("Patient does not have a valid OP Record. Please create one before proceeding."), title=_("No Valid OP Record Found"), primary_action={
	# 					"title": _("Create OP Record"),
	# 					"action": frappe.utils.get_link_to_form("OP Record", "New OP Record")
	# 				})
	# 		else:
	# 			op_record = frappe.get_doc("OP Record", self.op_record)
	# 			today = datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d").date()

	# 			if op_record.valid_till < today or op_record.status != "Open":
	# 				frappe.throw(msg=_("The selected OP Record is either expired or closed. Please select a valid OP Record."),title=_("No Valid OP Record Found"))

	# 			if op_record.patient != self.patient:
	# 				frappe.throw(msg=_("The selected OP Record does not belong to the patient. Please select a valid OP Record."), title=_("Invalid OP Record"))
