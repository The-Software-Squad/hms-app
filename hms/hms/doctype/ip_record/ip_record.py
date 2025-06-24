# Copyright (c) 2025, nani-samireddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class IPRecord(Document):
	def validate(self):
		if self.has_bed_changed():
			self.unassign_previous_bed()
			self.assign_bed()

	def before_save(self):
		if self.status == "Discharged" and not self.has_bed_changed():
			self.unassign_current_bed()

	def has_bed_changed(self):
		if self.is_new():
			return bool(self.bed)
		old = self.get_doc_before_save()
		return old and old.bed != self.bed

	def unassign_previous_bed(self):
		old = self.get_doc_before_save()
		if old and old.bed:
			self._unassign_bed(old.bed)

	def unassign_current_bed(self):
		if self.bed:
			self._unassign_bed(self.bed)

	def assign_bed(self):
		if not (self.bed and self.patient):
			return

		bed_doc = frappe.get_doc("Bed", self.bed)
		if bed_doc.current_patient and bed_doc.current_patient != self.patient:
			frappe.throw(f"Bed {self.bed} is already assigned to another patient.")

		bed_doc.current_patient = self.patient
		bed_doc.save(ignore_permissions=True)

	def _unassign_bed(self, bed_name):
		bed_doc = frappe.get_doc("Bed", bed_name)
		if bed_doc.current_patient == self.patient:
			bed_doc.current_patient = None
			bed_doc.save(ignore_permissions=True)
