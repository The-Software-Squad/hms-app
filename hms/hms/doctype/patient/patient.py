# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import getdate, nowdate
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe import _

class Patient(Document):
	def onload(self):
		# Load linked Address and Contact HTML (ERPNext integration)
		try:
			load_address_and_contact(self)
		except Exception:
			pass
	# def before_save(self):
	#     self.check_op_date_overlap_and_update_latest_expiry_date()

	def validate(self):
		# Normalize fields to align with Healthcare's Patient
		self.set_full_name()
		self._normalize_legacy_fields()

	def on_update(self):
		# Handle Customer linking/updates if enabled in Hospital Settings
		try:
			settings = frappe.get_single("Hospital Settings")
		except Exception:
			settings = None

			if settings and settings.get("link_customer_to_patient") and hasattr(self, "customer"):
				if not getattr(self, "customer", None):
					self._create_linked_customer(settings)
				else:
					self._update_linked_customer(settings)

		# Create or update linked Contact
		self.set_contact()

		# Optionally invite as website user
		if not getattr(self, "user_id", None) and getattr(self, "patient_email", None) and self.get("invite_user"):
			try:
				self.create_website_user()
			except Exception as e:
				frappe.log_error(f"Failed to create website user for Patient {self.name}: {e}", "HMS Patient")

	# Removed legacy Out Patient overlap/status helpers (superseded by Fee Validity)

	def set_full_name(self):
		"""Set patient_name from first/middle/last name if provided."""
		parts = []
		for f in ("first_name", "middle_name", "last_name"):
			val = (self.get(f) or "").strip()
			if val:
				parts.append(val)
		if parts:
			full = " ".join(parts)
			if self.patient_name != full:
				self.patient_name = full

	def _normalize_legacy_fields(self):
		"""Map legacy HMS fields to standard ones where appropriate."""
		# Gender mapping
		if not self.get("sex") and self.get("patient_gender"):
			self.sex = self.patient_gender
		# Mobile mapping
		if not self.get("mobile") and self.get("patient_phone_number"):
			self.mobile = self.patient_phone_number
		# Email mapping
		if not self.get("email") and self.get("patient_email"):
			# We don't create a separate 'email' field in schema, but
			# keep for future compatibility if introduced.
			pass

	# -----------------------------
	# ERPNext: Contact and Website User
	# -----------------------------
	def create_website_user(self):
		filters = {"email": self.patient_email}
		if self.mobile:
			filters["mobile_no"] = self.mobile
		users = frappe.db.get_all("User", fields=["name", "email", "mobile_no"], or_filters=filters)

		if users:
			msg = _("User exists with Email {0}").format(frappe.bold(users[0].email))
			if users[0].mobile_no:
				msg += _(", Mobile {0}").format(frappe.bold(users[0].mobile_no))
			msg += _("<br>Please check email/mobile or uncheck 'Invite as User' to skip creating User")
			frappe.throw(msg, frappe.DuplicateEntryError)

		user = frappe.get_doc(
			{
				"doctype": "User",
				"first_name": getattr(self, "first_name", None) or self.patient_name,
				"last_name": getattr(self, "last_name", None),
				"email": self.patient_email,
				"user_type": "Website User",
				"gender": getattr(self, "sex", None),
				"phone": getattr(self, "phone", None),
				"mobile_no": getattr(self, "mobile", None) or getattr(self, "patient_phone_number", None),
				"birth_date": getattr(self, "dob", None),
			}
		)
		user.flags.ignore_permissions = True
		user.enabled = True
		user.send_welcome_email = True
		user.insert(ignore_permissions=True)

		# Assign Patient role if available
		if frappe.db.exists("Role", "Patient"):
			try:
				user.add_roles("Patient")
			except Exception:
				pass

		self.db_set("user_id", user.name)

	def set_contact(self):
		"""Create or update a Contact linked to this Patient (and Customer if linked)."""
		contact_name = get_default_contact(self.doctype, self.name)
		if contact_name:
			old_doc = self.get_doc_before_save()
			if not old_doc:
				return
			if (
				old_doc.patient_email != self.patient_email
				or old_doc.patient_phone_number != getattr(self, "patient_phone_number", None)
			):
				self.update_contact(contact_name)
		else:
			# Try customer contact fallback
			cust = getattr(self, "customer", None)
			if cust:
				customer_contact = get_default_contact("Customer", cust)
				if customer_contact:
					self.update_contact(customer_contact)
					return
			# Create a new contact if we have any contact info
			if self.patient_email or getattr(self, "mobile", None) or getattr(self, "phone", None):
				contact = frappe.get_doc(
					{
						"doctype": "Contact",
						"first_name": getattr(self, "first_name", None) or self.patient_name,
						"middle_name": getattr(self, "middle_name", None),
						"last_name": getattr(self, "last_name", None),
						"gender": getattr(self, "sex", None),
						"is_primary_contact": 1,
					}
				)
				contact.append("links", dict(link_doctype="Patient", link_name=self.name))
				cust = getattr(self, "customer", None)
				if cust:
					contact.append("links", dict(link_doctype="Customer", link_name=cust))
				contact.insert(ignore_permissions=True)
				self.update_contact(contact.name)

	def update_contact(self, contact_name):
		contact = frappe.get_doc("Contact", contact_name)

		if not contact.has_link(self.doctype, self.name):
			contact.append("links", dict(link_doctype=self.doctype, link_name=self.name))

		# Update email
		if self.patient_email and self.patient_email != contact.email_id:
			for email in contact.email_ids:
				email.is_primary = True if email.email_id == self.patient_email else False
			contact.add_email(self.patient_email, is_primary=True)
			contact.set_primary_email()

			# Update mobile number
			_mob = getattr(self, "mobile", None) or getattr(self, "patient_phone_number", None)
			if _mob and _mob != contact.mobile_no:
				for mobile in contact.phone_nos:
					mobile.is_primary_mobile_no = True if mobile.phone == _mob else False
				contact.add_phone(_mob, is_primary_mobile_no=True)
				contact.set_primary("mobile_no")
			
			# Update phone number
			_ph = getattr(self, "phone", None)
			if _ph and _ph != contact.phone:
				for phone in contact.phone_nos:
					phone.is_primary_phone = True if phone.phone == _ph else False
				contact.add_phone(_ph, is_primary_phone=True)
				contact.set_primary("phone")

		contact.flags.skip_patient_update = True
		contact.save(ignore_permissions=True)

	# ERPNext Customer helpers
	def _ensure_customer_defaults(self, settings):
		defaults = {}
		try:
			from frappe.utils.nestedset import get_root_of
		except Exception:
			get_root_of = None

		defaults["customer_group"] = (
			settings.get("default_customer_group")
			or (get_root_of("Customer Group") if get_root_of else None)
			or "All Customer Groups"
		)
		defaults["territory"] = (
			settings.get("default_territory")
			or (get_root_of("Territory") if get_root_of else None)
			or "All Territories"
		)
		defaults["default_price_list"] = settings.get("default_price_list")
		return defaults

	def _create_linked_customer(self, settings):
		"""Create a Customer linked to this Patient."""
		defaults = self._ensure_customer_defaults(settings)
		try:
			customer = frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": self.patient_name,
					"customer_type": "Individual",
					"customer_group": self.customer_group or defaults.get("customer_group"),
					"territory": self.territory or defaults.get("territory"),
					"default_price_list": self.default_price_list or defaults.get("default_price_list"),
				}
			).insert(ignore_permissions=True, ignore_mandatory=True)

			if hasattr(self, "customer"):
				self.db_set("customer", customer.name)

			frappe.msgprint(
				_("Customer {0} created and linked to Patient").format(customer.name),
				alert=True,
			)
		except Exception as e:
			frappe.log_error(
				f"Failed to create Customer for Patient {self.name}: {e}",
				"HMS Patient",
			)

	def _update_linked_customer(self, settings):
		try:
			cust = getattr(self, "customer", None)
			if not cust:
				return
			customer = frappe.get_doc("Customer", cust)
		except Exception:
			# If missing, try to create
			return self._create_linked_customer(settings)

		# Update core fields
		dirty = False
		mapping = {
			"customer_name": self.patient_name,
			"customer_group": self.customer_group,
			"territory": self.territory,
			"default_price_list": self.default_price_list,
		}
		for key, val in mapping.items():
			if val and getattr(customer, key) != val:
				setattr(customer, key, val)
				dirty = True

		if dirty:
			try:
				customer.ignore_mandatory = True
				customer.save(ignore_permissions=True)
				frappe.msgprint(_("Customer {0} updated").format(customer.name), alert=True)
			except Exception as e:
				frappe.log_error(f"Failed to update Customer {customer.name}: {e}", "HMS Patient")
