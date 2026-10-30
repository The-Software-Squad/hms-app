import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class HealthcarePractitioner(Document):
	def validate(self):
		old = self.get_doc_before_save()
		if old is None and not self.is_new():
			old = frappe.db.get_value(
				self.doctype,
				self.name,
				["presence_status", "presence_updated_on", "presence_updated_by"],
				as_dict=True,
			)
		for field in ("presence_status", "presence_updated_on", "presence_updated_by"):
			expected = old.get(field) if old else ("Not Recorded" if field == "presence_status" else None)
			if (
				str(self.get(field) or "") != str(expected or "")
				and not frappe.flags.hms_practitioner_presence
			):
				frappe.throw(_("Use Hospital Live to report practitioner availability."))
		employee = frappe.get_doc("Employee", self.employee)
		if frappe.db.exists(
			"Healthcare Practitioner", {"employee": self.employee, "name": ["!=", self.name]}
		):
			frappe.throw(_("This employee already has a practitioner record."))
		if self.active and (
			not employee.employee_user or "Doctor" not in frappe.get_roles(employee.employee_user)
		):
			frappe.throw(_("An active practitioner must be linked to a user with the Doctor role."))
		self.practitioner_name = employee.employee_name
		self.user = employee.employee_user
		self.mobile = employee.phone_number
		self.email = employee.email
		self.designation = employee.designation
		if self.active and (
			employee.status != "Active" or not frappe.db.get_value("User", self.user, "enabled")
		):
			frappe.throw(_("An active practitioner requires an active employee and enabled user."))
		if cint(self.valid_days) < 0 or cint(self.max_visits) < 0:
			frappe.throw(_("Follow-up days and visits cannot be negative."))
