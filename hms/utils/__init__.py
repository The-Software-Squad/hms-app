import frappe

def has_active_out_patient_record(patient):
	'''Check if the patient has an active Out Patient Record'''
	patient_record = frappe.get_doc("Patient", patient)
	if not patient_record:
		return False
	
	# Check the child table for active Out Patient Record
	for op_record in patient_record.op_records:
		# child table field 'select' holds the status (Active/Expired)
		if getattr(op_record, "select", None) == "Active":
			return True
	
	return False
