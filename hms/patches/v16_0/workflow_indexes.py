import frappe


def execute():
	for doctype, fields, name in [
		("Patient Appointment", ["practitioner", "appointment_date", "status"], "hms_practitioner_booking"),
		("Patient Visit", ["patient", "visit_date"], "hms_patient_history"),
		("Patient Visit", ["follow_up_status", "follow_up"], "hms_follow_up_queue"),
		(
			"Fee Validity",
			["patient", "practitioner", "status", "start_date", "valid_till"],
			"hms_eligibility",
		),
		("IP Record", ["patient", "status"], "hms_active_admission"),
		("IP Record", ["bed", "status"], "hms_bed_admission"),
		("HMS Stock Movement", ["stock_lot", "posting_time"], "hms_lot_movements"),
		("HMS Invoice", ["patient", "status"], "hms_patient_balances"),
	]:
		frappe.db.add_index(doctype, fields, name)
