# Copyright (c) 2024, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class HospitalSettings(Document):
	def validate(self):
		seen, names = set(), set()
		for row in self.get("simulation_rooms") or []:
			if not row.enabled:
				continue
			if row.practitioner in seen or (row.room_name or "").strip().casefold() in names:
				frappe.throw(_("Use a different doctor and room name for each enabled simulation room."))
			if not (row.room_name or "").strip() or not 1 <= cint(row.waiting_seats) <= 24:
				frappe.throw(_("Each room needs a name and between 1 and 24 waiting seats."))
			if not frappe.db.get_value("Healthcare Practitioner", row.practitioner, "active"):
				frappe.throw(_("Choose an active practitioner for each simulation room."))
			seen.add(row.practitioner)
			names.add(row.room_name.strip().casefold())
