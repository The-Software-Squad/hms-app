"""Hospital Live permission, configuration and action-mapping regressions."""
from unittest import TestSuite, TextTestRunner
from unittest.mock import patch

import frappe
from frappe.utils import add_days, now_datetime, nowdate

from hms.api.hospital_live import set_availability, snapshot
from hms.tests.test_workflows import TestHMSWorkflows


class TestHospitalLive(TestHMSWorkflows):
	def setUp(self):
		super().setUp()
		self.settings.simulation_rooms = []
		self.settings.save()

	def test_snapshot_requires_hospital_role(self):
		for user in ("Guest", self.unrelated.name):
			frappe.set_user(user)
			with self.assertRaises(frappe.PermissionError):
				snapshot()

	def test_snapshot_tracks_saved_actions_and_excludes_finished_visits(self):
		self.settings.simulation_rooms = []
		self.settings.append(
			"simulation_rooms",
			dict(
				practitioner=self.practitioner.name, room_name="General Medicine", waiting_seats=6, enabled=1
			),
		)
		self.settings.save()
		self.schedule()
		appointment = self.appointment()
		before = snapshot()
		self.assertIn(appointment.name, [r.name for r in before["appointments"]])
		self.assertFalse(any(r.name == appointment.patient_visit for r in before["visits"]))
		visit = frappe.get_doc("Patient Visit", appointment.check_in())
		self.assertEqual(next(r for r in snapshot()["visits"] if r.name == visit.name).status, "Checked In")
		visit.status = "Under Consultation"
		visit.remarks = "Findings recorded"
		visit.save()
		data = snapshot()
		self.assertEqual(next(r for r in data["visits"] if r.name == visit.name).status, "Under Consultation")
		self.assertEqual(next(r for r in data["rooms"] if r["id"] == self.practitioner.name)["seats"], 6)
		self.assertNotIn("remarks", str(data))
		self.assertNotIn("patient_email", str(data))
		self.assertNotIn("mobile", str(data))
		visit.status = "Completed"
		visit.save()
		self.assertNotIn(visit.name, [r.name for r in snapshot()["visits"]])

	def test_availability_is_self_reported_and_expires_next_day(self):
		frappe.set_user(self.reception.name)
		with self.assertRaises(frappe.PermissionError):
			set_availability(self.practitioner.name, "Available")
		frappe.set_user(self.doctor_user.name)
		set_availability(self.practitioner.name, "Available")
		self.assertEqual(
			frappe.db.get_value("Healthcare Practitioner", self.practitioner.name, "presence_updated_by"),
			self.doctor_user.name,
		)
		self.assertEqual(
			next(r for r in snapshot()["rooms"] if r["id"] == self.practitioner.name)["availability"],
			"Available",
		)
		self.visit()  # Consultation validation must accept unchanged reported availability.
		frappe.db.set_value(
			"Healthcare Practitioner", self.practitioner.name, "presence_updated_on", add_days(nowdate(), -1)
		)
		self.assertEqual(
			next(r for r in snapshot()["rooms"] if r["id"] == self.practitioner.name)["availability"],
			"Not Recorded",
		)

	def test_presence_cannot_be_forged_through_master_save_or_another_doctor(self):
		self.practitioner.presence_status = "Available"
		with self.assertRaises(frappe.ValidationError):
			self.practitioner.save()
		frappe.set_user(self.doctor_user.name)
		with patch("hms.api.hospital_live.frappe.get_roles", return_value=["Doctor"]), patch(
			"hms.api.hospital_live.frappe.session", frappe._dict(user=self.unrelated.name)
		):
			with self.assertRaises(frappe.PermissionError):
				set_availability(self.practitioner.name, "Available")
		with self.assertRaises(frappe.ValidationError):
			set_availability(self.practitioner.name, "Present by GPS")

	def test_layout_rejects_duplicates_and_unsafe_seat_counts(self):
		for seats in (0, 25):
			self.settings.simulation_rooms = []
			self.settings.append(
				"simulation_rooms",
				dict(
					practitioner=self.practitioner.name,
					room_name="Consultation 01",
					waiting_seats=seats,
					enabled=1,
				),
			)
			with self.assertRaises(frappe.ValidationError):
				self.settings.save()
		self.settings.simulation_rooms = []
		for name in ("Room 01", "Room 02"):
			self.settings.append(
				"simulation_rooms",
				dict(practitioner=self.practitioner.name, room_name=name, waiting_seats=8, enabled=1),
			)
		with self.assertRaises(frappe.ValidationError):
			self.settings.save()

	def test_snapshot_uses_record_permissions_not_raw_unrestricted_queries(self):
		visit = self.visit()
		original = frappe.get_list

		def restricted(doctype, *args, **kwargs):
			if doctype == "Patient Visit":
				return []
			return original(doctype, *args, **kwargs)

		with patch("hms.api.hospital_live.frappe.get_list", side_effect=restricted):
			data = snapshot()
		self.assertNotIn(visit.name, [r.name for r in data["visits"]])
		frappe.set_user(self.pharmacist.name)
		data = snapshot()
		self.assertFalse(data["access"]["IP Record"])
		self.assertEqual(data["admissions"], [])

	def test_older_visits_are_review_exceptions_not_todays_waiting_people(self):
		visit = self.visit(visit_date=add_days(nowdate(), -1))
		data = snapshot()
		self.assertNotIn(visit.name, [r.name for r in data["visits"]])
		self.assertIn(visit.name, [r.name for r in data["older_visits"]])


def run():
	if frappe.local.site != "hms-workflow-test.localhost":
		raise RuntimeError("Refusing operational site")
	names = [name for name in TestHospitalLive.__dict__ if name.startswith("test_")]
	result = TextTestRunner(verbosity=2).run(TestSuite(TestHospitalLive(name) for name in names))
	if not result.wasSuccessful():
		raise RuntimeError("Hospital Live regressions failed")
	return dict(tests=result.testsRun, failures=0, errors=0)
