"""Create consistent user-guide examples on the disposable HMS workflow site."""
import hashlib
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate, now_datetime, nowdate


def seed():
	if frappe.local.site != "hms-workflow-test.localhost":
		raise RuntimeError("Guide fixtures are restricted to hms-workflow-test.localhost")
	frappe.set_user("Administrator")
	frappe.flags.in_test = True
	with patch("frappe.enqueue"), patch("frappe.sendmail"), patch(
		"frappe.core.doctype.user.user.throttle_user_creation"
	):
		from frappe.utils.password import update_password

		from hms.tests.test_workflows import TestHMSWorkflows

		case = TestHMSWorkflows()
		case.suffix = "guide-20261019"
		case.docs = []
		for gender in ("Male", "Female"):
			if not frappe.db.exists("Gender", gender):
				case.make("Gender", gender=gender)

		def staff(email, first, last, roles, gender="Male"):
			if frappe.db.exists("User", email):
				raise RuntimeError("User-guide example staff already exists: " + email)
			user = case.make(
				"User",
				email=email,
				first_name=first,
				last_name=last,
				user_type="System User",
				enabled=1,
				send_welcome_email=0,
				phone="+12025550101",
				gender=gender,
			)
			user.add_roles(*roles)
			return user

		case.department = case.make(
			"Department Type", department_name="General Medicine", out_patient_fees=500
		)
		case.role_type = case.make("Employee Role Type", role_name="Doctor")
		case.doctor_user = staff("alex.morgan@example.com", "Alex", "Morgan", ["Doctor"])
		case.employee = case.make(
			"Employee",
			employee_name="Dr Alex Morgan",
			employee_user=case.doctor_user.name,
			phone_number="+12025550101",
			email=case.doctor_user.name,
			gender="Male",
			designation=case.role_type.name,
			department=case.department.name,
		)
		case.practitioner = case.make(
			"Healthcare Practitioner", employee=case.employee.name, department=case.department.name, active=1
		)
		case.patient = case.make(
			"Patient",
			patient_name="Maya Patel",
			patient_phone_number="+12025550102",
			patient_email="maya.patel@example.com",
			patient_location="Mumbai",
			gender="Female",
			dob="1988-04-12",
		)
		case.settings = frappe.get_single("Hospital Settings")
		case.settings.hopital_name = "Riverbend Hospital"
		case.settings.enable_free_follow_ups = 1
		case.settings.valid_days = 7
		case.settings.max_visits = 2
		case.settings.currency = "INR"
		case.settings.save()
		manager = staff(
			"priya.sharma@example.com",
			"Priya",
			"Sharma",
			["System Manager", "Doctor", "Receptionist", "Pharmacist"],
			"Female",
		)
		update_password(manager.name, "HMS-Guide-Example-2026!")
		schedule = case.schedule()
		appointment = case.appointment(start_time="10:30:00", end_time="11:00:00")
		visit = case.visit(
			status="Under Consultation",
			remarks="Symptoms and medication history reviewed; follow-up planned.",
			follow_up=nowdate(),
		)
		initial = frappe.get_doc("Fee Validity", visit.fee_validity)
		timing = case.make(
			"Medicine Timing",
			timing_label="Morning",
			interval=1,
			timings=[{"start_time": "08:00:00", "end_time": "08:10:00"}],
		)
		provider = case.make(
			"Meds Provider",
			provider_name="Riverbend Medical Supplies",
			business_name="Riverbend Medical Supplies",
			contact_number="+12025550103",
			email="orders@riverbend.example.com",
			store_location="Mumbai",
		)
		item = case.make("Med Item", med_name="Paracetamol 500 mg tablet")
		medicine = case.make("Medicine", label="Paracetamol 500 mg", med_item=item.name)
		visit.append(
			"medication_schedule",
			{
				"medicine": medicine.name,
				"dose": "As prescribed",
				"timing": timing.name,
				"start_date": nowdate(),
				"duration_days": 7,
				"quantity": 7,
			},
		)
		visit.status = "Prescription Given"
		visit.save()
		intake = case.make(
			"Meds In take",
			provider=provider.name,
			in_take_date=nowdate(),
			invoice_number="INV-2026-1048",
			currency="INR",
			table_xxjy=[
				{
					"medical_item_name": item.name,
					"batch_number": "PCM-1026-A",
					"count": 40,
					"single_item_price": 1.2,
					"expires_at": add_days(nowdate(), 180),
				}
			],
		)
		posted_intake = case.make(
			"Meds In take",
			provider=provider.name,
			in_take_date=nowdate(),
			invoice_number="OPEN-2026-001",
			currency="INR",
			table_xxjy=[
				{
					"medical_item_name": item.name,
					"batch_number": "PCM-0726-B",
					"count": 40,
					"single_item_price": 1.2,
					"expires_at": add_days(nowdate(), 90),
				}
			],
		)
		posted_intake.post()
		posted_intake.reload()
		lot = posted_intake.table_xxjy[0].stock_lot
		sale = case.make(
			"Meds Out",
			patient=case.patient.name,
			patient_visit=visit.name,
			date=nowdate(),
			currency="INR",
			details=[
				{
					"stock_lot": lot,
					"med_quantity": 2,
					"med_price": 2,
					"prescription_row": visit.medication_schedule[0].name,
				}
			],
		)
		sale.post()
		sale.reload()
		adjustment = case.make(
			"HMS Stock Adjustment",
			stock_lot=lot,
			quantity=-1,
			reason="Stock count: one damaged tablet removed",
		)
		ward = case.make("Ward", ward_type="East Ward", capacity=3)
		bed = case.make("Bed", ward=ward.name, bed_number="A-01")
		transfer_bed = case.make("Bed", ward=ward.name, bed_number="A-02")
		admission = case.make(
			"IP Record",
			patient=case.patient.name,
			admission_date=nowdate(),
			bed=bed.name,
			practitioner=case.practitioner.name,
			status="Admitted",
		)
		care = case.make(
			"In Patient Treatment",
			in_patient=admission.name,
			date=nowdate(),
			practitioner=case.practitioner.name,
			medications_given="Medication administration and observations reviewed.",
			diagnosis_update="Patient observations recorded for the inpatient episode.",
			vitals=[{"time": "09:00:00", "temperature": 98.2, "pulse": 72, "respiratory_rate": 16}],
		)
		discharge = case.make(
			"Discharge Summary",
			in_patient=admission.name,
			discharge_date=nowdate(),
			practitioner=case.practitioner.name,
			final_diagnosis="Clinical review completed",
			discharge_notes="Discharge plan and medication instructions reviewed with the patient.",
			condition_at_discharge="Improved",
			follow_up=add_days(nowdate(), 3),
		)
		kind = case.make("Lab Report Type", lab_report_type_name="Complete Blood Count")
		file = case.make(
			"File",
			file_name="cbc-maya-patel.txt",
			content="Complete Blood Count\nMaya Patel\nReport received for clinician review.",
			is_private=1,
		)
		lab = case.make(
			"Lab Report",
			visit_reference=visit.name,
			report_type=kind.name,
			requested_on=nowdate(),
			received_on=nowdate(),
			report_file=file.file_url,
			status="Received",
		)
		invoice = case.make(
			"HMS Invoice",
			patient=case.patient.name,
			payer_name=case.patient.patient_name,
			invoice_date=nowdate(),
			currency="INR",
			items=[{"description": "Diagnostic services", "quantity": 1, "rate": 1000}],
		)
		invoice.issue()
		invoice.reload()
		payment = case.make(
			"Payment Recipit",
			patient=case.patient.name,
			payment_date=nowdate(),
			amount=1000,
			towards="Diagnostic services",
			currency="INR",
			allocations=[{"invoice": invoice.name, "amount": 1000}],
		)
		legacy = case.make(
			"Payment Recipit",
			patient=case.patient.name,
			payment_date=nowdate(),
			amount=500,
			towards="Consultation fee",
			currency="INR",
		)
		frappe.db.set_value(legacy.doctype, legacy.name, "status", "Legacy Recorded")
		duplicate = case.make(
			"Patient",
			patient_name=case.patient.patient_name,
			patient_phone_number=case.patient.patient_phone_number,
			patient_email="maya.patel+registration@example.com",
			patient_location="Mumbai",
		)
		from hms.api.mailer import prescription_version

		key = hashlib.sha256(
			f"{visit.name}:{prescription_version(visit)}:{case.patient.patient_email}".encode()
		).hexdigest()
		delivery = case.make(
			"HMS Medication Delivery",
			delivery_key=key,
			patient_visit=visit.name,
			patient=case.patient.name,
			recipient=case.patient.patient_email,
			requested_by=manager.name,
			requested_on=now_datetime(),
			status="Queued",
		)
		frappe.db.commit()
		frappe.flags.in_test = False
		return {
			"manager": manager.name,
			"patient": case.patient.name,
			"duplicate": duplicate.name,
			"employee": case.employee.name,
			"practitioner": case.practitioner.name,
			"schedule": schedule.name,
			"appointment": appointment.name,
			"visit": visit.name,
			"validity": initial.name,
			"intake": intake.name,
			"posted_intake": posted_intake.name,
			"lot": lot,
			"sale": sale.name,
			"adjustment": adjustment.name,
			"ward": ward.name,
			"bed": bed.name,
			"transfer_bed": transfer_bed.name,
			"admission": admission.name,
			"care": care.name,
			"discharge": discharge.name,
			"lab": lab.name,
			"invoice": invoice.name,
			"payment": payment.name,
			"legacy": legacy.name,
			"delivery": delivery.name,
			"timing": timing.name,
			"medicine": medicine.name,
		}
