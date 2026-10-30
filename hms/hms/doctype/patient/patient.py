import re

import frappe
from frappe import _
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class Patient(Document):
	def validate(self):
		self.patient_name = (self.patient_name or "").strip()
		self.patient_phone_number = (self.patient_phone_number or "").strip()
		self.patient_email = (self.patient_email or "").strip()
		if self.dob and getdate(self.dob) > getdate(nowdate()):
			frappe.throw(_("Date of birth cannot be in the future."))
		if not self.status:
			self.status = "Active"

	def onload(self):
		self.set_onload("duplicate_candidates", self._duplicates())

	def _duplicates(self):
		# Warn; a shared family contact is not sufficient evidence to merge people.
		phone = re.sub(r"\D", "", self.patient_phone_number or "")
		if not phone:
			return []
		candidates = frappe.get_list(
			"Patient",
			filters={"name": ["!=", self.name]},
			or_filters={"patient_phone_number": self.patient_phone_number, "patient_name": self.patient_name},
			fields=["name", "patient_name", "patient_phone_number", "dob"],
			limit_page_length=20,
		)
		return candidates

	def on_update(self):
		self.set_contact()
		if self.is_new() and self._duplicates():
			frappe.msgprint(
				_(
					"Possible existing patients share this name or phone. Review them before creating further records."
				),
				alert=True,
			)

	def set_contact(self):
		name = get_default_contact(self.doctype, self.name)
		if name:
			self.update_contact(name)
		else:
			contact = frappe.get_doc(
				{
					"doctype": "Contact",
					"first_name": self.patient_name,
					"is_primary_contact": 1,
					"links": [{"link_doctype": self.doctype, "link_name": self.name}],
				}
			).insert(ignore_permissions=True)
			self.update_contact(contact.name)

	def update_contact(self, name):
		contact = frappe.get_doc("Contact", name)
		contact.first_name, contact.middle_name, contact.last_name = self.patient_name, None, None
		if not contact.has_link(self.doctype, self.name):
			contact.append("links", {"link_doctype": self.doctype, "link_name": self.name})
		contact.set(
			"email_ids", [{"email_id": self.patient_email, "is_primary": 1}] if self.patient_email else []
		)
		contact.set(
			"phone_nos",
			[{"phone": self.patient_phone_number, "is_primary_mobile_no": 1, "is_primary_phone": 1}]
			if self.patient_phone_number
			else [],
		)
		contact.flags.skip_patient_update = True
		contact.save(ignore_permissions=True)

	def on_trash(self):
		for doctype in ("Patient Visit", "IP Record", "HMS Invoice", "Payment Recipit"):
			if frappe.db.exists(doctype, {"patient": self.name}):
				frappe.throw(
					_(
						"Patients with clinical or financial history must be retained. Use the duplicate merge workflow where appropriate."
					)
				)
