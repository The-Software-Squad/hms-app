import frappe

def daily():
	'''Runs daily once a day'''
	expire_out_patient_records()

def expire_out_patient_records():
	'''Updates Out Patient child records status to Expired if to date is older than current date'''
	from frappe.query_builder import DocType
	from frappe.query_builder import functions as fn
	
	today = frappe.utils.nowdate()
	
	# Define the child table
	OutPatient = DocType("Out Patient")
	frappe.log_error(f"Expiring Out Patient records as of {today}")
	
	try:
		count = (
			frappe.qb.from_(OutPatient)
			.select(fn.Count("*"))
			.where(
				(OutPatient["select"] == "Active") &
				(OutPatient.to < today) &
				(OutPatient.to.isnotnull())
			)
		).run()

		count = count[0][0] if count else 0
		frappe.log_error(f"Found {count} records to expire")

		if count == 0:
			return 0
		
		# Now update them
		(
			frappe.qb.update(OutPatient)
			.set(OutPatient["select"], "Expired")
			.where(
				(OutPatient["select"] == "Active") &
				(OutPatient.to < today) &
				(OutPatient.to.isnotnull())
			)
			.run()
		)
		
		frappe.db.commit()
		frappe.logger().info(f"Expired {count} Out Patient records")

		return count

	except Exception as e:
		frappe.log_error(f"Error expiring Out Patient records: {str(e)}")
		frappe.db.rollback()
		return 0
