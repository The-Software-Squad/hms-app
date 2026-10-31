"""Integration regressions. Refuse operational sites and never send real messages."""
from datetime import timedelta
from unittest import TestCase, TextTestRunner, defaultTestLoader
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate, nowdate

from hms.api import mailer
from hms.api import patient as patient_api
from hms.utils.icalender import generate_icalender_from_medicine_schedule, get_scheduled_days


class TestHMSWorkflows(TestCase):
	@classmethod
	def setUpClass(cls):
		if frappe.local.site != "hms-workflow-test.localhost":
			raise RuntimeError("Workflow tests only run on the isolated hms-workflow-test.localhost site.")
		# User/contact background jobs are fixture setup, not part of the HMS workflow.
		# Savepoint rollback does not discard Frappe's after-commit callbacks.
		cls.fixture_patches = [
			patch("frappe.enqueue"),
			patch("frappe.core.doctype.user.user.throttle_user_creation"),
		]
		for fixture_patch in cls.fixture_patches:
			fixture_patch.start()

	@classmethod
	def tearDownClass(cls):
		for fixture_patch in reversed(cls.fixture_patches):
			fixture_patch.stop()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.flags.in_test = True
		frappe.db.savepoint("hms_workflow_case")
		self.suffix = frappe.generate_hash(length=8)
		self.docs = []
		if not frappe.db.exists("Gender", "Male"):
			self.make("Gender", gender="Male")
		self.department = self.make(
			"Department Type", department_name="Training " + self.suffix, out_patient_fees=100
		)
		self.role_type = self.make("Employee Role Type", role_name="Doctor " + self.suffix)
		self.doctor_user = self.user("doctor", ["Doctor"])
		self.reception = self.user("reception", ["Receptionist"])
		self.pharmacist = self.user("pharmacist", ["Pharmacist"])
		self.unrelated = self.user("unrelated", [])
		self.employee = self.make(
			"Employee",
			employee_name="Fictional Doctor " + self.suffix,
			employee_user=self.doctor_user.name,
			phone_number="+12025550101",
			email=self.doctor_user.name,
			gender="Male",
			designation=self.role_type.name,
			department=self.department.name,
			salary=50000,
		)
		self.practitioner = self.make(
			"Healthcare Practitioner", employee=self.employee.name, department=self.department.name, active=1
		)
		self.patient = self.make(
			"Patient",
			patient_name="Fictional Patient " + self.suffix,
			patient_phone_number="+12025550102",
			patient_email="patient-" + self.suffix + "@example.invalid",
			patient_location="Training City",
		)
		self.settings = frappe.get_single("Hospital Settings")
		self.settings.enable_free_follow_ups = 0
		self.settings.valid_days = 7
		self.settings.max_visits = 1
		self.settings.currency = "INR"
		self.settings.save()

	def tearDown(self):
		frappe.set_user("Administrator")
		if getattr(self, "committed_for_concurrency", False):
			frappe.db.rollback()
		else:
			frappe.db.rollback(save_point="hms_workflow_case")
		for doctype, name in self.docs:
			frappe.clear_document_cache(doctype, name)
		frappe.flags.in_test = False

	def make(self, doctype, **values):
		doc = frappe.get_doc(dict(doctype=doctype, **values)).insert(ignore_permissions=True)
		self.docs.append((doctype, doc.name))
		return doc

	def user(self, label, roles):
		user = self.make(
			"User",
			email=f"{label}-{self.suffix}@example.invalid",
			first_name="Fictional " + label,
			user_type="System User",
			enabled=1,
			send_welcome_email=0,
			phone="+12025550101",
			gender="Male",
		)
		if roles:
			user.add_roles(*roles)
		return user

	def visit(self, **values):
		return self.make(
			"Patient Visit",
			**dict(
				dict(
					patient=self.patient.name,
					doctor=self.practitioner.name,
					department=self.department.name,
					visit_date=nowdate(),
					status="Checked In",
				),
				**values,
			),
		)

	def schedule(self):
		return self.make(
			"Practitioner Schedule",
			practitioner=self.practitioner.name,
			time_slots=[
				{"day_of_week": getdate().strftime("%A"), "start_time": "09:00:00", "end_time": "17:00:00"}
			],
		)

	def appointment(self, **values):
		return self.make(
			"Patient Appointment",
			**dict(
				dict(
					patient=self.patient.name,
					practitioner=self.practitioner.name,
					appointment_date=nowdate(),
					start_time="10:00:00",
				),
				**values,
			),
		)

	def admission(self):
		ward = self.make("Ward", ward_type="Training Ward " + self.suffix, capacity=3)
		bed = self.make("Bed", ward=ward.name, bed_number="1")
		ip = self.make(
			"IP Record",
			patient=self.patient.name,
			admission_date=nowdate(),
			bed=bed.name,
			practitioner=self.practitioner.name,
			status="Admitted",
		)
		return ip, bed, ward

	def stock(self):
		provider = self.make(
			"Meds Provider",
			provider_name="Supplier " + self.suffix,
			business_name="Training Supplier",
			contact_number="+12025550103",
			email="supplier@example.invalid",
			store_location="Training City",
		)
		item = self.make("Med Item", med_name="Training Item " + self.suffix)
		intake = self.make(
			"Meds In take",
			provider=provider.name,
			in_take_date=nowdate(),
			table_xxjy=[
				{
					"medical_item_name": item.name,
					"batch_number": "TRAINING",
					"count": 10,
					"single_item_price": 5,
					"expires_at": add_days(nowdate(), 30),
				}
			],
		)
		intake.post()
		intake.reload()
		return intake, item, intake.table_xxjy[0].stock_lot

	def test_practitioner_mapping_and_contact_sync(self):
		self.assertEqual(self.practitioner.user, self.doctor_user.name)
		from frappe.contacts.doctype.contact.contact import get_default_contact

		contact = frappe.get_doc("Contact", get_default_contact("Patient", self.patient.name))
		self.assertEqual(contact.mobile_no, self.patient.patient_phone_number)
		self.patient.patient_phone_number = "+12025550104"
		self.patient.patient_email = ""
		self.patient.save()
		contact.reload()
		self.assertEqual(contact.mobile_no, "+12025550104")
		self.assertFalse(contact.email_id)

	def test_history_and_mail_denied_to_unrelated_and_guest(self):
		visit = self.visit()
		for user in [self.unrelated.name, "Guest", self.reception.name]:
			frappe.set_user(user)
			with self.assertRaises(frappe.PermissionError):
				patient_api.get_previous_patient_visits(self.patient.name)
			with self.assertRaises(frappe.PermissionError):
				mailer.send_medication_mail(visit.name)
		frappe.set_user(self.doctor_user.name)
		self.assertEqual(
			patient_api.get_previous_patient_visits(self.patient.name)[0].doctor_name,
			self.employee.employee_name,
		)

	def test_employee_private_fields(self):
		from frappe.client import get

		frappe.set_user(self.reception.name)
		doc = get("Employee", self.employee.name)
		self.assertFalse(doc.get("salary"))
		self.assertFalse(frappe.has_permission("In Patient Treatment", "write"))
		self.assertTrue(frappe.has_permission("Patient Visit", "create"))

	def test_appointment_normalization_overlap_and_checkin_retry(self):
		self.schedule()
		appt = self.appointment()
		self.assertEqual(str(appt.end_time), "10:30:00")
		with self.assertRaises(frappe.ValidationError):
			self.appointment(start_time="10:00:00")
		frappe.set_user(self.reception.name)
		first = appt.check_in()
		second = appt.check_in()
		self.assertEqual(first, second)
		self.assertEqual(frappe.db.count("Patient Visit", {"appointment": appt.name}), 1)

	def test_outside_shift_and_cancel_after_schedule_change(self):
		schedule = self.schedule()
		with self.assertRaises(frappe.ValidationError):
			self.appointment(start_time="18:00:00")
		appt = self.appointment()
		schedule.time_slots[0].end_time = "09:30:00"
		schedule.save()
		appt.status = "Cancelled"
		appt.save()
		self.assertEqual(appt.status, "Cancelled")

	def test_fee_cap_disable_and_cancellation(self):
		first = self.visit()
		self.assertFalse(first.fee_validity)
		self.assertTrue(first.invoice)
		self.settings.enable_free_follow_ups = 1
		self.settings.save()
		initial = self.visit()
		follow = self.visit()
		extra = self.visit()
		self.assertEqual(initial.fee_validity, follow.fee_validity)
		self.assertNotEqual(initial.fee_validity, extra.fee_validity)
		self.assertFalse(follow.invoice)
		follow.status = "Cancelled / No Show"
		follow.save()
		self.assertEqual(frappe.db.get_value("Fee Validity", initial.fee_validity, "visited"), 0)
		initial.reload()
		initial.status = "Cancelled / No Show"
		initial.save()
		self.assertFalse(initial.fee_validity)

	def test_visit_identity_and_completion(self):
		visit = self.visit()
		visit.visit_date = add_days(nowdate(), 1)
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		visit.reload()
		visit.status = "Completed"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		visit.reload()
		visit.status = "Completed"
		visit.remarks = "Fictional examination documented."
		visit.save()
		self.assertTrue(visit.completed_on)
		visit.remarks = "Corrected fictional note."
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		visit.reload()
		visit.remarks = "Corrected fictional note."
		visit.correction_reason = "Correct training transcription"
		visit.save()

	def test_admission_transfer_discharge_and_reopen(self):
		ip, bed, ward = self.admission()
		bed.reload()
		self.assertEqual(bed.current_admission, ip.name)
		other = self.make("Bed", ward=ward.name, bed_number="2")
		ip.bed = other.name
		ip.save()
		bed.reload()
		other.reload()
		self.assertFalse(bed.current_patient)
		self.assertEqual(other.current_patient, self.patient.name)
		summary = self.make(
			"Discharge Summary",
			in_patient=ip.name,
			discharge_date=nowdate(),
			practitioner=self.practitioner.name,
			condition_at_discharge="Improved",
			discharge_notes="Fictional training instructions.",
		)
		summary.finalize()
		other.reload()
		ip.reload()
		self.assertEqual(ip.status, "Discharged")
		self.assertFalse(other.current_patient)
		ip.reopen("Training readmission correction")
		other.reload()
		self.assertEqual(other.current_admission, ip.name)

	def test_bed_ownership_and_deletion_protection(self):
		ip, bed, ward = self.admission()
		with self.assertRaises(frappe.ValidationError):
			self.make(
				"IP Record",
				patient=self.patient.name,
				admission_date=nowdate(),
				bed=bed.name,
				practitioner=self.practitioner.name,
			)
		with self.assertRaises(frappe.ValidationError):
			frappe.delete_doc("IP Record", ip.name)
		bed.reload()
		bed.current_patient = None
		with self.assertRaises(frappe.ValidationError):
			bed.save()

	def test_lab_association_and_private_file(self):
		visit = self.visit()
		kind = self.make("Lab Report Type", lab_report_type_name="Training Lab " + self.suffix)
		report = self.make(
			"Lab Report", visit_reference=visit.name, report_type=kind.name, requested_on=nowdate()
		)
		self.assertEqual(report.patient, self.patient.name)
		report.report_file = '"><img src=x onerror=alert(1)>'
		with self.assertRaises(frappe.ValidationError):
			report.save()
		report.report_file = None
		report.status = "Received"
		with self.assertRaises(frappe.ValidationError):
			report.save()

	def test_calendar_elapsed_duration_and_email_idempotency(self):
		self.assertEqual([d.day for d in get_scheduled_days("2026-10-18", 2, 7)], [18, 20, 22, 24])
		timing = self.make(
			"Medicine Timing",
			timing_label="Training alternate " + self.suffix,
			interval=2,
			timings=[{"start_time": "09:00:00", "end_time": "09:10:00"}],
		)
		medicine = self.make("Medicine", label="Training Medicine " + self.suffix)
		visit = self.visit(
			status="Prescription Given",
			medication_schedule=[
				{
					"medicine": medicine.name,
					"dose": "Training dose",
					"timing": timing.name,
					"start_date": nowdate(),
					"duration_days": 7,
				}
			],
		)
		ics = generate_icalender_from_medicine_schedule(visit.medication_schedule)
		self.assertEqual(ics.count("BEGIN:VEVENT"), 4)
		with patch("frappe.sendmail", return_value=frappe._dict(name="fictional-mail-queue")) as send:
			one = mailer.send_medication_mail(visit.name)
			two = mailer.send_medication_mail(visit.name)
			self.assertEqual(send.call_count, 1)
			self.assertTrue(two["duplicate"])
			self.assertNotIn("icalender_string", one)

	def test_stock_post_dispense_return_and_caps(self):
		intake, item, lot = self.stock()
		intake.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 10)
		frappe.set_user(self.pharmacist.name)
		sale = self.make(
			"Meds Out",
			meds_out_type="Outside Patient",
			customer_name="Fictional Customer",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 3, "med_price": 8}],
		)
		sale.post()
		sale.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 7)
		ret = self.make(
			"Meds Out",
			transaction_type="Return",
			return_origin="Uncollected",
			return_disposition="Restock",
			return_reason="Uncollected medicines inspected at the pharmacy",
			return_against=sale.name,
			meds_out_type="Outside Patient",
			customer_name="Fictional Customer",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 2, "med_price": 8}],
		)
		ret.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 9)
		self.assertEqual(frappe.db.get_value("HMS Invoice", sale.invoice, "credited_amount"), 16)
		extra = self.make(
			"Meds Out",
			transaction_type="Return",
			return_origin="Uncollected",
			return_disposition="Restock",
			return_reason="Uncollected medicines inspected at the pharmacy",
			return_against=sale.name,
			meds_out_type="Outside Patient",
			customer_name="Fictional Customer",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 2, "med_price": 8}],
		)
		with self.assertRaises(frappe.ValidationError):
			extra.post()

	def test_stock_negative_and_posted_edit(self):
		intake, item, lot = self.stock()
		bad = self.make(
			"Meds Out",
			meds_out_type="Outside Patient",
			customer_name="Fictional Customer",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 11, "med_price": 8}],
		)
		with self.assertRaises(frappe.ValidationError):
			bad.post()
		intake.reload()
		intake.table_xxjy[0].count = 20
		with self.assertRaises(frappe.ValidationError):
			intake.save()

	def test_invoice_payment_refund_immutability(self):
		visit = self.visit()
		invoice = frappe.get_doc("HMS Invoice", visit.invoice)
		self.assertEqual(invoice.total, 100)
		payment = self.make(
			"Payment Recipit",
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=100,
			towards="Training consultation",
			allocations=[{"invoice": invoice.name, "amount": 100}],
		)
		payment.post()
		payment.post()
		invoice.reload()
		self.assertEqual(invoice.status, "Paid")
		payment.amount = 200
		with self.assertRaises(frappe.ValidationError):
			payment.save()
		payment.reload()
		refund = self.make(
			"Payment Recipit",
			transaction_type="Refund",
			reference_receipt=payment.name,
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=50,
			towards="Training partial refund",
			allocations=[{"invoice": invoice.name, "amount": 50}],
		)
		refund.post()
		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 50)
		extra = self.make(
			"Payment Recipit",
			transaction_type="Refund",
			reference_receipt=payment.name,
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=60,
			towards="Invalid excess refund",
			allocations=[{"invoice": invoice.name, "amount": 60}],
		)
		with self.assertRaises(frappe.ValidationError):
			extra.post()

	def test_followup_booking_sets_and_restores_queue_state(self):
		self.schedule()
		visit = self.visit(follow_up=nowdate())
		appt = self.appointment(follow_up_visit=visit.name)
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "follow_up_status"), "Scheduled")
		appt.status = "Cancelled"
		appt.save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "follow_up_status"), "Pending")

	def test_patient_dates_updated_without_read_writes(self):
		visit = self.visit(follow_up=add_days(nowdate(), 2))
		self.patient.reload()
		self.assertEqual(getdate(self.patient.follow_up), getdate(add_days(nowdate(), 2)))
		visit.follow_up = None
		visit.save()
		self.patient.reload()
		self.assertFalse(self.patient.follow_up)
		before = self.patient.modified
		self.patient.run_method("onload")
		self.patient.reload()
		self.assertEqual(before, self.patient.modified)

	def test_validity_cancellation_terminal_and_policy_override(self):
		self.settings.enable_free_follow_ups = 1
		self.settings.save()
		self.practitioner.followup_policy = "Disabled"
		self.practitioner.save()
		self.assertFalse(self.visit().fee_validity)
		self.practitioner.followup_policy = "Enabled"
		self.practitioner.save()
		visit = self.visit()
		name = visit.fee_validity
		visit.status = "Cancelled / No Show"
		visit.save()
		fv = frappe.get_doc("Fee Validity", name)
		fv.save()
		self.assertEqual(fv.status, "Cancelled")

	def test_private_report_review_blocks_reception(self):
		visit = self.visit()
		kind = self.make("Lab Report Type", lab_report_type_name="Training report " + self.suffix)
		file = self.make(
			"File", file_name="training-report.txt", content="Fictional laboratory result", is_private=1
		)
		report = self.make(
			"Lab Report",
			visit_reference=visit.name,
			report_type=kind.name,
			requested_on=nowdate(),
			received_on=nowdate(),
			report_file=file.file_url,
			status="Received",
		)
		frappe.set_user(self.reception.name)
		report.status = "Reviewed"
		with self.assertRaises(frappe.PermissionError):
			report.save()
		frappe.set_user(self.doctor_user.name)
		report.reload()
		report.status = "Reviewed"
		report.save()
		self.assertEqual(report.reviewed_by, self.doctor_user.name)

	def test_prescription_dispensing_checks_quantity_and_item(self):
		intake, item, lot = self.stock()
		timing = self.make(
			"Medicine Timing",
			timing_label="Training timing " + self.suffix,
			interval=1,
			timings=[{"start_time": "08:00:00", "end_time": "08:10:00"}],
		)
		medicine = self.make("Medicine", label="Mapped Medicine " + self.suffix, med_item=item.name)
		visit = self.visit(
			status="Prescription Given",
			medication_schedule=[
				{
					"medicine": medicine.name,
					"dose": "Training dose",
					"timing": timing.name,
					"start_date": nowdate(),
					"duration_days": 2,
					"quantity": 2,
				}
			],
		)
		from hms.api.pharmacy import prescription_lines

		frappe.set_user(self.reception.name)
		with self.assertRaises(frappe.PermissionError):
			prescription_lines(visit.name)
		frappe.set_user(self.pharmacist.name)
		options = prescription_lines(visit.name)
		self.assertEqual(options["lines"][0]["medical_item"], item.name)
		self.assertEqual(options["lines"][0]["remaining"], 2)
		sale = self.make(
			"Meds Out",
			patient=self.patient.name,
			patient_visit=visit.name,
			date=nowdate(),
			details=[
				{
					"stock_lot": lot,
					"med_quantity": 2,
					"med_price": 5,
					"prescription_row": visit.medication_schedule[0].name,
				}
			],
		)
		sale.post()
		self.assertEqual(prescription_lines(visit.name)["lines"], [])
		extra = self.make(
			"Meds Out",
			patient=self.patient.name,
			patient_visit=visit.name,
			date=nowdate(),
			details=[
				{
					"stock_lot": lot,
					"med_quantity": 1,
					"med_price": 5,
					"prescription_row": visit.medication_schedule[0].name,
				}
			],
		)
		with self.assertRaises(frappe.ValidationError):
			extra.post()

	def test_partial_post_failure_rolls_back_stock(self):
		intake, item, lot = self.stock()
		other = self.make(
			"HMS Stock Adjustment", stock_lot=lot, quantity=2, reason="Fictional opening adjustment"
		)
		other.post()
		intake2 = self.make(
			"Meds In take",
			provider=intake.provider,
			in_take_date=nowdate(),
			table_xxjy=[
				{
					"medical_item_name": item.name,
					"batch_number": "SECOND",
					"count": 1,
					"single_item_price": 5,
					"expires_at": add_days(nowdate(), 30),
				}
			],
		)
		intake2.post()
		intake2.reload()
		lot2 = intake2.table_xxjy[0].stock_lot
		sale = self.make(
			"Meds Out",
			meds_out_type="Outside Patient",
			customer_name="Training Customer",
			date=nowdate(),
			details=[
				{"stock_lot": lot, "med_quantity": 2, "med_price": 5},
				{"stock_lot": lot2, "med_quantity": 2, "med_price": 5},
			],
		)
		with self.assertRaises(frappe.ValidationError):
			sale.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 12)
		self.assertFalse(frappe.db.exists("HMS Stock Movement", {"source_name": sale.name}))

	def test_expired_lot_and_intake_cancellation(self):
		intake, item, lot = self.stock()
		frappe.db.set_value("HMS Stock Lot", lot, "expires_at", add_days(nowdate(), -1))
		sale = self.make(
			"Meds Out",
			meds_out_type="Outside Patient",
			customer_name="Fictional Customer",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 1, "med_price": 5}],
		)
		with self.assertRaises(frappe.ValidationError):
			sale.post()
		intake.cancel_intake("Training duplicate receipt")
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 0)

	def test_same_name_patients_have_separate_invoices(self):
		other = self.make(
			"Patient",
			patient_name=self.patient.patient_name,
			patient_phone_number="+12025550108",
			patient_location="Another Training City",
		)
		one = self.visit()
		two = self.visit(patient=other.name)
		self.assertNotEqual(one.invoice, two.invoice)
		self.assertEqual(frappe.db.get_value("HMS Invoice", one.invoice, "patient"), self.patient.name)
		self.assertEqual(frappe.db.get_value("HMS Invoice", two.invoice, "patient"), other.name)

	def test_merge_is_explicit_and_audited(self):
		from hms.api.registration import merge_patients

		other = self.make(
			"Patient",
			patient_name=self.patient.patient_name,
			patient_phone_number="+12025550108",
			patient_location="Training City",
		)
		frappe.set_user(self.reception.name)
		with self.assertRaises(frappe.PermissionError):
			merge_patients(other.name, self.patient.name, "Reviewed training duplicate")
		frappe.set_user("Administrator")
		merge_patients(other.name, self.patient.name, "Reviewed training duplicate")
		self.assertFalse(frappe.db.exists("Patient", other.name))
		self.assertTrue(
			frappe.db.exists(
				"HMS Patient Merge", {"source_patient": other.name, "target_patient": self.patient.name}
			)
		)

	def test_calculated_invoice_balance_cannot_be_forged(self):
		visit = self.visit()
		invoice = frappe.get_doc("HMS Invoice", visit.invoice)
		invoice.paid_amount = 10000
		with self.assertRaises(frappe.ValidationError):
			invoice.save()

	def test_mail_queue_failure_does_not_leave_duplicate_guard(self):
		timing = self.make(
			"Medicine Timing",
			timing_label="Training mail " + self.suffix,
			interval=1,
			timings=[{"start_time": "09:00:00", "end_time": "09:10:00"}],
		)
		medicine = self.make("Medicine", label="Mail Medicine " + self.suffix)
		visit = self.visit(
			status="Prescription Given",
			medication_schedule=[
				{
					"medicine": medicine.name,
					"dose": "Training dose",
					"timing": timing.name,
					"start_date": nowdate(),
					"duration_days": 1,
				}
			],
		)
		with patch("frappe.sendmail", return_value=None):
			with self.assertRaises(frappe.ValidationError):
				mailer.send_medication_mail(visit.name)
		self.assertFalse(frappe.db.exists("HMS Medication Delivery", {"patient_visit": visit.name}))

	def test_legacy_migration_preserves_receipt_and_requires_reconciliation(self):
		from hms.patches.v16_0 import capture_legacy_workflows, preserve_legacy_workflows

		visit = self.visit()
		payment = self.make(
			"Payment Recipit",
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=100,
			towards="Fictional historical collection",
			allocations=[],
		)
		with patch.object(frappe.db, "has_column", return_value=False):
			capture_legacy_workflows.execute()
		preserve_legacy_workflows.execute()
		payment.reload()
		self.assertEqual(payment.status, "Legacy Recorded")
		self.assertEqual(payment.amount, 100)
		payment.append("allocations", {"invoice": visit.invoice, "amount": 100})
		payment.save()
		payment.post()
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "status"), "Paid")

	def test_concurrent_booking_commits_only_one(self):
		from concurrent.futures import ThreadPoolExecutor

		self.schedule()
		# Committed fictional fixtures are needed by independent database connections.
		frappe.db.commit()
		self.committed_for_concurrency = True
		site, patient, practitioner, department = (
			frappe.local.site,
			self.patient.name,
			self.practitioner.name,
			self.department.name,
		)

		def book(index):
			frappe.init(site)
			frappe.connect()
			frappe.set_user("Administrator")
			frappe.flags.in_test = True
			try:
				frappe.get_doc(
					{
						"doctype": "Patient Appointment",
						"patient": patient,
						"practitioner": practitioner,
						"department": department,
						"appointment_date": nowdate(),
						"start_time": "11:00:00",
						"end_time": "11:30:00",
					}
				).insert(set_name=f"TRAINING-{self.suffix}-{index}")
				frappe.db.commit()
				return "booked"
			except (frappe.ValidationError, frappe.QueryDeadlockError):
				frappe.db.rollback()
				return "conflict"
			finally:
				frappe.destroy()

		with ThreadPoolExecutor(max_workers=2) as pool:
			results = list(pool.map(book, range(2)))
		frappe.db.rollback()
		self.assertEqual(sorted(results), ["booked", "conflict"])
		self.assertEqual(frappe.db.count("Patient Appointment", {"practitioner": practitioner}), 1)

	def concurrent_posts(self, doctype, names):
		from concurrent.futures import ThreadPoolExecutor

		frappe.db.commit()
		self.committed_for_concurrency = True
		site = frappe.local.site

		def post(name):
			frappe.init(site)
			frappe.connect()
			frappe.set_user("Administrator")
			frappe.flags.in_test = True
			try:
				frappe.get_doc(doctype, name).post()
				frappe.db.commit()
				return "posted"
			except (frappe.ValidationError, frappe.QueryDeadlockError):
				frappe.db.rollback()
				return "rejected"
			finally:
				frappe.destroy()

		with ThreadPoolExecutor(max_workers=2) as pool:
			results = sorted(pool.map(post, names))
		frappe.db.rollback()
		return results

	def test_concurrent_stock_cannot_go_negative(self):
		_, _, lot = self.stock()
		adjustments = [
			self.make("HMS Stock Adjustment", stock_lot=lot, quantity=-7, reason="Training concurrent count")
			for _ in range(2)
		]
		self.assertEqual(
			self.concurrent_posts("HMS Stock Adjustment", [d.name for d in adjustments]),
			["posted", "rejected"],
		)
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity", for_update=True), 3)

	def test_concurrent_payments_cannot_overpay(self):
		visit = self.visit()
		payments = [
			self.make(
				"Payment Recipit",
				patient=self.patient.name,
				payment_date=nowdate(),
				amount=100,
				towards="Training concurrent payment",
				allocations=[{"invoice": visit.invoice, "amount": 100}],
			)
			for _ in range(2)
		]
		self.assertEqual(
			self.concurrent_posts("Payment Recipit", [d.name for d in payments]), ["posted", "rejected"]
		)
		self.assertEqual(
			frappe.db.get_value("HMS Invoice", visit.invoice, "paid_amount", for_update=True), 100
		)

	def test_legacy_dispensing_cannot_repost(self):
		_, _, lot = self.stock()
		out = self.make(
			"Meds Out",
			meds_out_type="Existing Patient",
			patient=self.patient.name,
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 1, "med_price": 5}],
		)
		frappe.db.set_value("Meds Out", out.name, "status", "Legacy")
		out.reload()
		with self.assertRaises(frappe.ValidationError):
			out.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 10)

	def test_reception_doctor_and_pharmacist_can_complete_core_actions(self):
		self.schedule()
		frappe.set_user(self.reception.name)
		appointment = frappe.get_doc(
			{
				"doctype": "Patient Appointment",
				"patient": self.patient.name,
				"practitioner": self.practitioner.name,
				"department": self.department.name,
				"appointment_date": nowdate(),
				"start_time": "12:00:00",
				"end_time": "12:30:00",
			}
		).insert()
		visit_name = appointment.check_in()
		frappe.set_user(self.doctor_user.name)
		visit = frappe.get_doc("Patient Visit", visit_name)
		visit.remarks, visit.status = "Fictional training findings", "Completed"
		visit.save()
		frappe.set_user(self.reception.name)
		payment = frappe.get_doc(
			{
				"doctype": "Payment Recipit",
				"patient": self.patient.name,
				"payment_date": nowdate(),
				"amount": 100,
				"towards": "Training consultation",
				"allocations": [{"invoice": visit.invoice, "amount": 100}],
			}
		).insert()
		payment.post()
		frappe.set_user("Administrator")
		_, _, lot = self.stock()
		frappe.set_user(self.pharmacist.name)
		out = frappe.get_doc(
			{
				"doctype": "Meds Out",
				"meds_out_type": "Existing Patient",
				"patient": self.patient.name,
				"date": nowdate(),
				"details": [{"stock_lot": lot, "med_quantity": 1, "med_price": 5}],
			}
		).insert()
		out.post()
		self.assertEqual(out.status, "Posted")

	def test_followup_queue_excludes_missing_and_future_dates(self):
		self.visit()
		self.visit(follow_up=add_days(nowdate(), 3))
		due = self.visit(follow_up=nowdate())
		rows = frappe.get_list(
			"Patient Visit",
			filters=[
				["Patient Visit", "patient", "=", self.patient.name],
				["Patient Visit", "follow_up", "is", "set"],
				["Patient Visit", "follow_up", "<=", nowdate()],
				["Patient Visit", "follow_up_status", "in", ["Pending", "Contacted"]],
			],
			fields=["name", "follow_up"],
		)
		self.assertEqual([row.name for row in rows], [due.name])

	def test_appointment_visit_link_cannot_be_injected(self):
		self.schedule()
		visit = self.visit()
		with self.assertRaises(frappe.ValidationError):
			self.make(
				"Patient Appointment",
				patient=self.patient.name,
				practitioner=self.practitioner.name,
				department=self.department.name,
				appointment_date=nowdate(),
				start_time="12:00:00",
				end_time="12:30:00",
				patient_visit=visit.name,
			)

	def test_delivery_refresh_uses_saved_queue_reference(self):
		from frappe.utils import now_datetime

		visit = self.visit()
		delivery = self.make(
			"HMS Medication Delivery",
			delivery_key=frappe.generate_hash(length=64),
			patient_visit=visit.name,
			patient=self.patient.name,
			recipient=self.patient.patient_email,
			requested_by="Administrator",
			requested_on=now_datetime(),
			status="Queued",
		)
		delivery.email_queue = "forged-unrelated-queue"
		delivery.refresh_status()
		self.assertFalse(frappe.db.get_value(delivery.doctype, delivery.name, "email_queue"))

	def test_treatment_author_is_server_assigned(self):
		admission, _, _ = self.admission()
		treatment = self.make(
			"In Patient Treatment", in_patient=admission.name, date=nowdate(), recorded_by=self.unrelated.name
		)
		self.assertEqual(treatment.recorded_by, "Administrator")
		treatment.recorded_by = self.unrelated.name
		with self.assertRaises(frappe.ValidationError):
			treatment.save()

	def test_lab_file_cannot_be_reused_from_another_report(self):
		visit = self.visit()
		kind = self.make("Lab Report Type", lab_report_type_name="Private training " + self.suffix)
		file = self.make(
			"File", file_name="private-training.txt", content="Fictional private lab result", is_private=1
		)
		report = self.make(
			"Lab Report",
			visit_reference=visit.name,
			report_type=kind.name,
			requested_on=nowdate(),
			report_file=file.file_url,
		)
		self.assertEqual(frappe.db.get_value("File", file.name, "attached_to_name"), report.name)
		with self.assertRaises(frappe.PermissionError):
			self.make(
				"Lab Report",
				visit_reference=visit.name,
				report_type=kind.name,
				requested_on=nowdate(),
				report_file=file.file_url,
			)

	def test_public_record_names_use_independent_readable_sequences(self):
		intake, _, lot = self.stock()
		self.assertRegex(intake.name, r"^HMS-INT-\d{4}-\d{5,}$")
		self.assertRegex(lot, r"^HMS-LOT-\d{5,}$")
		first = self.make("HMS Stock Adjustment", stock_lot=lot, quantity=1, reason="Count correction")
		first.post()
		visit = self.visit()
		self.assertRegex(visit.invoice, r"^HMS-INV-\d{4}-\d{5,}$")
		second = self.make("HMS Stock Adjustment", stock_lot=lot, quantity=1, reason="Count correction")
		self.assertEqual(int(second.name.rsplit("-", 1)[1]), int(first.name.rsplit("-", 1)[1]) + 1)
		movement = frappe.db.get_value("HMS Stock Movement", {"source_name": first.name}, "name")
		self.assertRegex(movement, r"^HMS-MOV-\d{4}-\d{5,}$")
		admission, _, _ = self.admission()
		care = self.make("In Patient Treatment", in_patient=admission.name, date=nowdate())
		self.assertEqual(care.name, admission.name + "-CARE-001")

	def test_followup_contact_save_accepts_unchanged_serialized_clinical_date(self):
		visit = self.visit(status="Completed", remarks="Symptoms reviewed", follow_up=nowdate())
		payload = frappe.parse_json(frappe.as_json(visit.as_dict()))
		payload["follow_up_status"] = "Contacted"
		payload["follow_up_notes"] = "Appointment availability discussed"
		frappe.get_doc(payload).save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "follow_up_status"), "Contacted")
		changed = frappe.get_doc("Patient Visit", visit.name)
		changed.follow_up = add_days(nowdate(), 1)
		with self.assertRaises(frappe.ValidationError):
			changed.save()

	def test_readable_name_migration_preserves_stock_sources_and_idempotency(self):
		from hms.patches.v16_0 import readable_record_names

		intake, _, lot = self.stock()
		old = frappe.generate_hash(length=10)
		frappe.rename_doc(
			"Meds In take", intake.name, old, force=True, show_alert=False, rebuild_search=False
		)
		movement = frappe.db.get_value("HMS Stock Movement", {"source_name": old}, "name")
		frappe.db.set_value(
			"HMS Stock Movement", movement, "event_key", f"Intake:{old}:{intake.table_xxjy[0].name}"
		)
		before = frappe.db.count("HMS Stock Movement", {"stock_lot": lot})
		readable_record_names.execute()
		new = frappe.db.get_value("Meds In take", {"legacy_id": old}, "name")
		self.assertRegex(new, r"^HMS-INT-\d{4}-\d{5,}$")
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "intake"), new)
		self.assertEqual(frappe.db.get_value("Intake Medical Item", intake.table_xxjy[0].name, "parent"), new)
		self.assertEqual(frappe.db.get_value("HMS Stock Movement", movement, "source_name"), new)
		self.assertEqual(
			frappe.db.get_value("HMS Stock Movement", movement, "event_key"),
			f"Intake:{new}:{intake.table_xxjy[0].name}",
		)
		frappe.get_doc("Meds In take", new).post()
		self.assertEqual(frappe.db.count("HMS Stock Movement", {"stock_lot": lot}), before)
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 10)
		readable_record_names.execute()
		self.assertEqual(frappe.db.get_value("Meds In take", {"legacy_id": old}, "name"), new)

	def test_sidebar_groups_cover_all_hms_record_types(self):
		from frappe.desk.doctype.sidebar.sidebar import resolve_sidebar

		from hms.module_map import MODULES

		links = []
		for module in MODULES:
			sidebar = resolve_sidebar(module, frappe.session.user)
			self.assertIsNotNone(sidebar, module)
			self.assertFalse(sidebar.computed)
			self.assertEqual(sidebar.items[-1]["link_to"], "hms-guide")
			sections = [row for row in sidebar.items if row["type"] == "Section Break"]
			self.assertTrue(all(row["collapsible"] for row in sections))
			module_links = [row for row in sidebar.items if row["type"] == "Link"]
			self.assertEqual(
				len({(row["link_type"], row["link_to"]) for row in module_links}), len(module_links)
			)
			links.extend(module_links)
		linked_doctypes = {row["link_to"] for row in links if row["link_type"] == "DocType"}
		expected = set(
			frappe.get_all("DocType", filters={"module": ["in", MODULES], "istable": 0}, pluck="name")
		)
		self.assertEqual(linked_doctypes, expected - {"Medical Department", "Patient Care Type"})
		for row in links:
			self.assertTrue(frappe.db.exists(row["link_type"], row["link_to"]), row["link_to"])

	def test_sidebar_preserves_role_permissions(self):
		from frappe.desk.doctype.sidebar.sidebar import resolve_sidebar

		from hms.module_map import MODULES

		for user, visible, hidden in (
			(
				self.reception,
				{"Patient", "Patient Appointment", "IP Record"},
				{"Meds In take", "Hospital Settings"},
			),
			(
				self.doctor_user,
				{"Patient Visit", "In Patient Treatment", "Lab Report"},
				{"Meds Out", "Hospital Settings"},
			),
			(
				self.pharmacist,
				{"Meds In take", "Meds Out", "HMS Stock Lot"},
				{"Patient", "Hospital Settings"},
			),
		):
			with self.subTest(user=user.name):
				frappe.set_user(user.name)
				items = []
				for module in MODULES:
					sidebar = resolve_sidebar(module, user.name)
					if sidebar:
						self.assertFalse(sidebar.computed)
						items.extend(sidebar.items)
				targets = {row.get("link_to") for row in items}
				self.assertTrue(visible.issubset(targets))
				self.assertTrue(hidden.isdisjoint(targets))
				self.assertIn("hms-guide", targets)
				for row in items:
					if row.get("link_type") == "DocType":
						self.assertTrue(frappe.has_permission(row["link_to"], "read", user=user.name))
		frappe.set_user("Administrator")

	def prescribed_visit(self, item=None, status="Prescription Given"):
		timing = self.make(
			"Medicine Timing",
			timing_label="Morning " + self.suffix,
			interval=1,
			timings=[{"start_time": "08:00:00", "end_time": "08:15:00"}],
		)
		medicine = self.make("Medicine", label="Paracetamol 500 mg " + self.suffix, med_item=item)
		visit = self.visit(
			status=status,
			remarks="Consultation findings recorded",
			medication_schedule=[
				{
					"medicine": medicine.name,
					"dose": "As prescribed",
					"timing": timing.name,
					"start_date": nowdate(),
					"duration_days": 2,
					"quantity": 2,
				}
			],
		)
		return visit, medicine

	def test_prescribed_medicine_mapping_and_identity_are_frozen(self):
		first = self.make("Med Item", med_name="Paracetamol 500 mg " + self.suffix)
		second = self.make("Med Item", med_name="Paracetamol 650 mg " + self.suffix)
		visit, medicine = self.prescribed_visit(first.name, status="Completed")
		frappe.set_user(self.reception.name)
		for field, value in (
			("med_item", second.name),
			("label", "Different medicine"),
			("composition", "Different composition"),
		):
			with self.subTest(field=field):
				medicine.reload()
				medicine.set(field, value)
				with self.assertRaises(frappe.ValidationError):
					medicine.save()
		medicine.reload()
		medicine.description = "Store according to pack instructions"
		medicine.save()
		frappe.set_user("Administrator")
		with self.assertRaises(frappe.ValidationError):
			frappe.rename_doc("Medicine", medicine.name, "Renamed medicine " + self.suffix, force=True)
		self.assertEqual(frappe.db.get_value("Medicine", medicine.name, "med_item"), first.name)
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Completed")
		unused = self.make("Medicine", label="New catalogue entry " + self.suffix, med_item=first.name)
		unused.med_item = second.name
		unused.save()
		self.assertEqual(unused.med_item, second.name)

	def test_appointment_progress_is_derived_from_consultation(self):
		self.schedule()
		source = self.visit(follow_up=nowdate())
		appointment = self.appointment(follow_up_visit=source.name)
		frappe.set_user(self.reception.name)
		visit_name = appointment.check_in()
		for state in ("In Service", "Completed", "No Show"):
			appointment.reload()
			appointment.status = state
			with self.assertRaises(frappe.ValidationError):
				appointment.save()
		self.assertEqual(frappe.db.get_value("Patient Appointment", appointment.name, "status"), "Checked In")
		self.assertEqual(frappe.db.get_value("Patient Visit", source.name, "follow_up_status"), "Scheduled")
		frappe.set_user(self.doctor_user.name)
		visit = frappe.get_doc("Patient Visit", visit_name)
		visit.status = "Under Consultation"
		visit.save()
		self.assertEqual(frappe.db.get_value("Patient Appointment", appointment.name, "status"), "In Service")
		visit.remarks = "Findings recorded"
		visit.status = "Completed"
		visit.save()
		self.assertEqual(frappe.db.get_value("Patient Appointment", appointment.name, "status"), "Completed")
		self.assertEqual(frappe.db.get_value("Patient Visit", source.name, "follow_up_status"), "Closed")
		frappe.set_user(self.reception.name)
		for state in ("In Service", "Cancelled"):
			appointment.reload()
			appointment.status = state
			with self.assertRaises(frappe.ValidationError):
				appointment.save()

	def test_cancellation_requires_resolved_lab_requests(self):
		self.schedule()
		appointment = self.appointment()
		visit_name = appointment.check_in()
		visit = frappe.get_doc("Patient Visit", visit_name)
		kind = self.make("Lab Report Type", lab_report_type_name="Complete Blood Count " + self.suffix)
		report = self.make(
			"Lab Report", visit_reference=visit.name, report_type=kind.name, requested_on=nowdate()
		)
		frappe.set_user(self.reception.name)
		appointment.reload()
		appointment.status = "Cancelled"
		with self.assertRaises(frappe.ValidationError):
			appointment.save()
		self.assertEqual(frappe.db.get_value("Patient Appointment", appointment.name, "status"), "Checked In")
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Checked In")
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "status"), "Issued")
		frappe.set_user(self.doctor_user.name)
		report.status = "Cancelled"
		report.save()
		frappe.set_user(self.reception.name)
		appointment.reload()
		appointment.status = "Cancelled"
		appointment.save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Cancelled / No Show")
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "status"), "Void")

	def test_new_lab_request_requires_active_consultation(self):
		kind = self.make("Lab Report Type", lab_report_type_name="Complete Blood Count " + self.suffix)
		for status in ("Completed", "Cancelled / No Show"):
			visit = self.visit(status=status, remarks="Findings recorded")
			with self.assertRaises(frappe.ValidationError):
				self.make(
					"Lab Report", visit_reference=visit.name, report_type=kind.name, requested_on=nowdate()
				)

	def test_cancellation_requires_return_of_posted_medicines(self):
		_, item, lot = self.stock()
		visit, _ = self.prescribed_visit(item.name)
		row = visit.medication_schedule[0]
		sale = self.make(
			"Meds Out",
			meds_out_type="Existing Patient",
			patient=self.patient.name,
			patient_visit=visit.name,
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 2, "med_price": 5, "prescription_row": row.name}],
		)
		sale.post()
		visit.status = "Cancelled / No Show"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Prescription Given")
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 8)
		returned = self.make(
			"Meds Out",
			transaction_type="Return",
			return_origin="Uncollected",
			return_disposition="Restock",
			return_reason="Uncollected medicines inspected at the pharmacy",
			return_against=sale.name,
			meds_out_type="Existing Patient",
			patient=self.patient.name,
			patient_visit=visit.name,
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": 2, "med_price": 5, "prescription_row": row.name}],
		)
		returned.post()
		visit.reload()
		visit.status = "Cancelled / No Show"
		visit.save()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 10)
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "status"), "Void")
		self.assertEqual(frappe.db.get_value("Meds Out", sale.name, "status"), "Posted")

	def test_cancellation_retains_full_credit_and_refund_history(self):
		visit = self.visit()
		invoice = frappe.get_doc("HMS Invoice", visit.invoice)
		receipt = self.make(
			"Payment Recipit",
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=100,
			towards="Consultation",
			allocations=[{"invoice": invoice.name, "amount": 100}],
		)
		receipt.post()
		credit = self.make(
			"HMS Invoice",
			patient=self.patient.name,
			payer_name=self.patient.patient_name,
			invoice_date=nowdate(),
			invoice_type="Credit",
			credit_against=invoice.name,
			currency="INR",
			items=[{"description": "Cancelled consultation", "quantity": 1, "rate": 100}],
		)
		credit.issue()
		visit.status = "Cancelled / No Show"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Checked In")
		refund = self.make(
			"Payment Recipit",
			transaction_type="Refund",
			reference_receipt=receipt.name,
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=100,
			towards="Consultation refund",
			allocations=[{"invoice": invoice.name, "amount": 100}],
		)
		refund.post()
		visit.reload()
		visit.status = "Cancelled / No Show"
		visit.save()
		visit.save()
		invoice.reload()
		self.assertEqual(invoice.credited_amount, 100)
		self.assertEqual(invoice.paid_amount, 0)
		self.assertEqual(invoice.outstanding_amount, 0)
		self.assertNotEqual(invoice.status, "Void")
		self.assertEqual(frappe.db.get_value("HMS Invoice", credit.name, "credit_against"), invoice.name)
		self.assertEqual(frappe.db.get_value("Payment Recipit", refund.name, "status"), "Posted")

	def test_partial_credit_does_not_silently_cancel_remaining_charge(self):
		visit = self.visit()
		credit = self.make(
			"HMS Invoice",
			patient=self.patient.name,
			payer_name=self.patient.patient_name,
			invoice_date=nowdate(),
			invoice_type="Credit",
			credit_against=visit.invoice,
			currency="INR",
			items=[{"description": "Partial charge reduction", "quantity": 1, "rate": 40}],
		)
		credit.issue()
		visit.status = "Cancelled / No Show"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Checked In")
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "outstanding_amount"), 60)

	def test_backdated_followup_uses_actual_visit_date_and_cap(self):
		self.settings.enable_free_follow_ups = 1
		self.settings.valid_days = 7
		self.settings.max_visits = 2
		self.settings.save()
		initial = self.visit(visit_date=add_days(nowdate(), -10))
		first = self.visit(visit_date=add_days(nowdate(), -9))
		second = self.visit(visit_date=add_days(nowdate(), -8))
		extra = self.visit(visit_date=add_days(nowdate(), -7))
		self.assertEqual(frappe.db.get_value("Fee Validity", initial.fee_validity, "status"), "Expired")
		self.assertEqual(first.fee_validity, initial.fee_validity)
		self.assertEqual(second.fee_validity, initial.fee_validity)
		self.assertFalse(first.invoice)
		self.assertFalse(second.invoice)
		self.assertTrue(extra.invoice)
		self.assertNotEqual(extra.fee_validity, initial.fee_validity)

	def test_backdated_followup_never_reuses_cancelled_window(self):
		self.settings.enable_free_follow_ups = 1
		self.settings.valid_days = 7
		self.settings.max_visits = 2
		self.settings.save()
		initial = self.visit(visit_date=add_days(nowdate(), -10))
		window = initial.fee_validity
		initial.status = "Cancelled / No Show"
		initial.save()
		next_visit = self.visit(visit_date=add_days(nowdate(), -9))
		self.assertNotEqual(next_visit.fee_validity, window)
		self.assertTrue(next_visit.invoice)

	def test_admission_requires_a_bed_and_tracks_changes(self):
		with self.assertRaises(frappe.ValidationError):
			self.make(
				"IP Record",
				patient=self.patient.name,
				admission_date=nowdate(),
				practitioner=self.practitioner.name,
				status="Admitted",
			)
		for doctype in ("IP Record", "Hospital Settings", "Healthcare Practitioner", "Practitioner Schedule"):
			self.assertTrue(frappe.get_meta(doctype).track_changes, doctype)
		admission, _, _ = self.admission()
		admission.bed = None
		with self.assertRaises(frappe.ValidationError):
			admission.save()

	def test_payment_currency_must_match_invoice(self):
		visit = self.visit()
		payment = self.make(
			"Payment Recipit",
			patient=self.patient.name,
			payment_date=nowdate(),
			amount=100,
			towards="Training cross-currency payment",
			currency="USD",
			allocations=[{"invoice": visit.invoice, "amount": 100}],
		)
		with self.assertRaises(frappe.ValidationError):
			payment.post()
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "paid_amount"), 0)

	def departure(self, source, **values):
		from frappe.utils import now_datetime

		return self.make(
			"HMS Patient Departure",
			**dict(
				dict(
					source_doctype=source.doctype,
					source_name=source.name,
					outcome="Left During Care",
					departed_on=now_datetime(),
					reason="Patient chose to leave before further care",
					clinical_notes="Current observations and advice recorded; advised to return for further assessment.",
				),
				**values,
			),
		)

	def pharmacy_sale(self, quantity=4):
		_, _, lot = self.stock()
		sale = self.make(
			"Meds Out",
			meds_out_type="Outside Patient",
			customer_name="Arjun Rao",
			date=nowdate(),
			details=[{"stock_lot": lot, "med_quantity": quantity, "med_price": 5}],
		)
		sale.post()
		return sale, lot

	def handover(self, sale, lot, quantity):
		return self.make(
			"HMS Pharmacy Collection",
			source_sale=sale.name,
			recipient_name="Arjun Rao",
			details=[{"stock_lot": lot, "quantity": quantity}],
		)

	def pharmacy_return(self, sale, lot, quantity, **values):
		return self.make(
			"Meds Out",
			**dict(
				dict(
					transaction_type="Return",
					return_against=sale.name,
					meds_out_type=sale.meds_out_type,
					customer_name=sale.customer_name,
					patient=sale.patient,
					patient_visit=sale.patient_visit,
					date=nowdate(),
					return_origin="Collected",
					return_disposition="Quarantine",
					return_reason="Returned pack requires inspection of packaging and storage conditions",
					details=[{"stock_lot": lot, "med_quantity": quantity, "med_price": 5}],
				),
				**values,
			),
		)

	def test_departure_before_seen_uses_cancellation_without_completing_care(self):
		self.schedule()
		appointment = self.appointment()
		visit = frappe.get_doc("Patient Visit", appointment.check_in())
		frappe.set_user(self.reception.name)
		departure = self.departure(visit, outcome="Left Before Seen", clinical_notes=None)
		departure.finalize()
		departure.finalize()
		visit.reload()
		self.assertEqual(visit.status, "Cancelled / No Show")
		self.assertEqual(visit.departure_outcome, "Left Before Seen")
		self.assertFalse(visit.completed_on)
		self.assertEqual(frappe.db.get_value("Patient Appointment", appointment.name, "status"), "Cancelled")
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "status"), "Void")

	def test_departure_during_care_keeps_invoice_and_requires_clinical_staff(self):
		self.schedule()
		appointment = self.appointment()
		visit = frappe.get_doc("Patient Visit", appointment.check_in())
		visit.status, visit.remarks = "Under Consultation", "Findings recorded"
		visit.save()
		before = self.departure(visit, outcome="Left Before Seen", clinical_notes=None)
		with self.assertRaises(frappe.ValidationError):
			before.finalize()
		frappe.set_user(self.reception.name)
		departure = self.departure(visit, clinical_notes=None)
		with self.assertRaises(frappe.PermissionError):
			departure.finalize()
		frappe.set_user(self.doctor_user.name)
		departure.clinical_notes = "Assessment and advice recorded. Patient declined further assessment."
		departure.save()
		departure.finalize()
		visit.reload()
		self.assertEqual(visit.status, "Closed Early")
		self.assertEqual(visit.remarks, "Findings recorded")
		self.assertFalse(visit.completed_on)
		self.assertEqual(
			frappe.db.get_value("Patient Appointment", appointment.name, "status"), "Closed Early"
		)
		self.assertEqual(frappe.db.get_value("HMS Invoice", visit.invoice, "outstanding_amount"), 100)
		visit.status = "Completed"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		departure.reason = "Overwrite"
		with self.assertRaises(frappe.ValidationError):
			departure.save()

	def test_departure_pending_results_requires_owner_and_actual_resolution(self):
		visit = self.visit(status="Under Consultation", remarks="Examination recorded")
		kind = self.make("Lab Report Type", lab_report_type_name="Complete Blood Count " + self.suffix)
		lab = self.make(
			"Lab Report", visit_reference=visit.name, report_type=kind.name, requested_on=nowdate()
		)
		departure = self.departure(visit)
		with self.assertRaises(frappe.ValidationError):
			departure.finalize()
		self.assertEqual(frappe.db.get_value("Patient Visit", visit.name, "status"), "Under Consultation")
		departure.reload()
		departure.responsible_practitioner, departure.review_due_on = self.practitioner.name, nowdate()
		departure.save()
		departure.finalize()
		self.assertEqual(departure.review_status, "Pending")
		with self.assertRaises(frappe.ValidationError):
			departure.resolve_review()
		with self.assertRaises(frappe.ValidationError):
			self.make("Lab Report", visit_reference=visit.name, report_type=kind.name, requested_on=nowdate())
		with self.assertRaises(frappe.ValidationError):
			frappe.delete_doc("Lab Report", lab.name)
		lab.status = "Cancelled"
		lab.save()
		departure.resolve_review()
		departure.resolve_review()
		self.assertEqual(frappe.db.get_value(departure.doctype, departure.name, "review_status"), "Resolved")

	def test_departure_fields_and_closed_early_cannot_be_forged(self):
		visit = self.visit()
		visit.departure_outcome = "Transferred"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		visit.reload()
		visit.status = "Closed Early"
		with self.assertRaises(frappe.ValidationError):
			visit.save()
		with self.assertRaises(frappe.ValidationError):
			self.departure(visit, status="Finalized")

	def test_inpatient_departure_releases_bed_and_retains_history_on_reopen(self):
		ip, bed, ward = self.admission()
		departure = self.departure(ip, outcome="Transferred")
		departure.finalize()
		departure.finalize()
		ip.reload()
		bed.reload()
		ward.reload()
		self.assertEqual(ip.status, "Discharged")
		self.assertFalse(ip.discharge_summary)
		self.assertFalse(bed.current_admission)
		self.assertEqual(ward.total_occupied, 0)
		summary = self.make(
			"Discharge Summary",
			in_patient=ip.name,
			discharge_date=nowdate(),
			condition_at_discharge="Improved",
			discharge_notes="Transfer already recorded; verify closure cannot be replaced.",
		)
		with self.assertRaises(frappe.ValidationError):
			summary.finalize()
		with self.assertRaises(frappe.ValidationError):
			self.make("In Patient Treatment", in_patient=ip.name, date=nowdate())
		ip.reopen("Patient returned for continued inpatient care")
		ip.reload()
		bed.reload()
		self.assertFalse(ip.departure_record)
		self.assertEqual(bed.current_admission, ip.name)
		self.assertEqual(frappe.db.get_value(departure.doctype, departure.name, "status"), "Finalized")

	def test_inpatient_departure_rolls_back_bed_release_on_failure(self):
		from hms.hms_inpatient.doctype.ip_record.ip_record import IPRecord

		ip, bed, _ = self.admission()
		departure = self.departure(ip, outcome="Admission Cancelled")
		original = IPRecord.on_update

		def fail(doc):
			original(doc)
			raise RuntimeError("Interrupted after bed update")

		with patch.object(IPRecord, "on_update", fail), self.assertRaises(RuntimeError):
			departure.finalize()
		self.assertEqual(frappe.db.get_value("Bed", bed.name, "current_admission"), ip.name)
		self.assertEqual(frappe.db.get_value("IP Record", ip.name, "status"), "Admitted")
		self.assertEqual(frappe.db.get_value(departure.doctype, departure.name, "status"), "Draft")

	def test_admission_cancellation_cannot_erase_started_treatment(self):
		ip, bed, _ = self.admission()
		self.make("In Patient Treatment", in_patient=ip.name, date=nowdate())
		departure = self.departure(ip, outcome="Admission Cancelled")
		with self.assertRaises(frappe.ValidationError):
			departure.finalize()
		self.assertEqual(frappe.db.get_value("Bed", bed.name, "current_admission"), ip.name)

	def test_pharmacy_partial_handovers_are_capped_and_immutable(self):
		sale, lot = self.pharmacy_sale()
		self.assertEqual(sale.collection_tracking, 1)
		frappe.set_user(self.pharmacist.name)
		handover = self.handover(sale, lot, 2)
		handover.post()
		handover.post()
		self.assertEqual(frappe.db.get_value("Meds Out", sale.name, "collection_status"), "Partly Collected")
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 6)
		extra = self.handover(sale, lot, 3)
		with self.assertRaises(frappe.ValidationError):
			extra.post()
		handover.recipient_name = "Change name"
		with self.assertRaises(frappe.ValidationError):
			handover.save()
		last = self.handover(sale, lot, 2)
		last.post()
		self.assertEqual(frappe.db.get_value("Meds Out", sale.name, "collection_status"), "Collected")

	def test_collected_returns_quarantine_and_release_or_dispose_explicitly(self):
		sale, lot = self.pharmacy_sale()
		self.handover(sale, lot, 4).post()
		returned = self.pharmacy_return(sale, lot, 3)
		returned.post()
		returned.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 6)
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "quarantined_quantity"), 3)
		movement = frappe.db.get_value(
			"HMS Stock Movement",
			{"source_doctype": "Meds Out", "source_name": returned.name},
			["stock_bucket", "quantity"],
			as_dict=True,
		)
		self.assertEqual((movement.stock_bucket, movement.quantity), ("Quarantine", 3))
		self.assertEqual(frappe.db.get_value("HMS Invoice", sale.invoice, "credited_amount"), 15)
		release = self.make(
			"HMS Stock Adjustment",
			stock_lot=lot,
			quantity=2,
			adjustment_type="Release Quarantine",
			reason="Sealed packaging and storage conditions inspected",
		)
		release.post()
		release.post()
		disposal = self.make(
			"HMS Stock Adjustment",
			stock_lot=lot,
			quantity=1,
			adjustment_type="Dispose Quarantine",
			reason="Packaging damaged; removed from usable inventory",
		)
		disposal.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 8)
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "quarantined_quantity"), 0)
		self.assertEqual(
			frappe.db.get_value(
				"Intake Medical Item",
				frappe.db.get_value("HMS Stock Lot", lot, "intake_row"),
				"available_stock",
			),
			8,
		)

	def test_return_origin_cannot_restock_unreturned_or_handed_medicines(self):
		sale, lot = self.pharmacy_sale()
		self.handover(sale, lot, 2).post()
		bad = self.pharmacy_return(sale, lot, 3, return_origin="Uncollected", return_disposition="Restock")
		with self.assertRaises(frappe.ValidationError):
			bad.post()
		bad = self.pharmacy_return(sale, lot, 3)
		with self.assertRaises(frappe.ValidationError):
			bad.post()
		uncollected = self.pharmacy_return(
			sale, lot, 2, return_origin="Uncollected", return_disposition="Restock"
		)
		uncollected.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 8)
		with self.assertRaises(frappe.ValidationError):
			self.handover(sale, lot, 1).post()
		self.pharmacy_return(sale, lot, 2).post()
		self.assertEqual(frappe.db.get_value("Meds Out", sale.name, "collection_status"), "Returned")
		self.assertEqual(sale.collection_items(), [])

	def test_pharmacy_historical_sales_never_invent_collection_history(self):
		sale, lot = self.pharmacy_sale()
		frappe.db.set_value("Meds Out", sale.name, {"collection_tracking": 0, "collection_status": None})
		with self.assertRaises(frappe.ValidationError):
			self.handover(sale, lot, 1).post()
		returned = self.pharmacy_return(sale, lot, 1)
		with self.assertRaises(frappe.ValidationError):
			returned.post()
		returned.reload()
		returned.return_origin = "Legacy Not Tracked"
		returned.save()
		returned.post()
		self.assertEqual(frappe.db.get_value("Meds Out", sale.name, "collection_status"), "Not Tracked")
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 6)

	def test_quarantine_release_failure_is_atomic_and_expired_release_is_blocked(self):
		from hms.stock import move

		sale, lot = self.pharmacy_sale()
		self.handover(sale, lot, 4).post()
		self.pharmacy_return(sale, lot, 2).post()
		release = self.make(
			"HMS Stock Adjustment",
			stock_lot=lot,
			quantity=2,
			adjustment_type="Release Quarantine",
			reason="Pack inspection completed",
		)

		def fail_available(*args, **kwargs):
			if kwargs.get("bucket") != "Quarantine":
				raise RuntimeError("Interrupted before available-stock update")
			return move(*args, **kwargs)

		with patch(
			"hms.hms_pharmacy.doctype.hms_stock_adjustment.hms_stock_adjustment.move",
			side_effect=fail_available,
		), self.assertRaises(RuntimeError):
			release.post()
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "quarantined_quantity"), 2)
		self.assertEqual(frappe.db.get_value("HMS Stock Lot", lot, "available_quantity"), 6)
		frappe.db.set_value("HMS Stock Lot", lot, "expires_at", add_days(nowdate(), -1))
		with self.assertRaises(frappe.ValidationError):
			release.post()
		with self.assertRaises(frappe.ValidationError):
			self.pharmacy_return(sale, lot, 1, return_disposition="Restock").post()

	def test_handover_permissions_and_server_owned_fields(self):
		sale, lot = self.pharmacy_sale()
		handover = self.handover(sale, lot, 1)
		frappe.set_user(self.reception.name)
		with self.assertRaises(frappe.PermissionError):
			handover.post()
		frappe.set_user("Administrator")
		sale.reload()
		sale.collection_status = "Collected"
		with self.assertRaises(frappe.ValidationError):
			sale.save()
		with self.assertRaises(frappe.ValidationError):
			self.make(
				"HMS Pharmacy Collection",
				source_sale=sale.name,
				recipient_name="Arjun Rao",
				handed_by=self.pharmacist.name,
				details=[{"stock_lot": lot, "quantity": 1}],
			)


def run():
	if frappe.local.site != "hms-workflow-test.localhost":
		raise RuntimeError("Refusing to run on an operational site.")
	result = TextTestRunner(verbosity=2).run(defaultTestLoader.loadTestsFromTestCase(TestHMSWorkflows))
	if not result.wasSuccessful():
		raise RuntimeError(f"{len(result.failures)} failures; {len(result.errors)} errors")
	return {"tests": result.testsRun, "failures": 0, "errors": 0}
