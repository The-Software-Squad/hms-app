import frappe

def daily():
	'''Runs daily once a day'''
	send_op_expiration_remainder()

def send_op_expiration_remainder():
	try:
		# Check if the patient doctype is present.
		if not frappe.db.exists("Patient") or not frappe.db.exists("WhatsApp Settings"):
			return

		# Get all the patients whose OP is going to expire in 3 days.
		patients = frappe.get_all("Patient", filters={"op_expiry_date": frappe.utils.add_days(frappe.utils.nowdate(), 3)}, fields=["name", "op_expiry_date"])
		if not patients:
			return

		# Get the 

	except Exception as e:
		frappe.error_log(f"Error in send_op_expiration_remainder: {e}")

