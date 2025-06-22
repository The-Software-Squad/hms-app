import frappe

def daily():
	'''Runs daily once a day'''
	close_expired_op_records()

def close_expired_op_records():
	'''Closes all OP Records that have expired'''
	today = frappe.utils.nowdate()
	expired_op_records = frappe.get_all(
		"OP Record",
		filters={
			"valid_till": ["<", today],
			"status": "Open"
		},
		fields=["name"]
	)

	if not expired_op_records:
		return

	for op_record in expired_op_records:
		doc = frappe.get_doc("OP Record", op_record.name)
		doc.status = "Closed"
		doc.save()
		frappe.db.commit()