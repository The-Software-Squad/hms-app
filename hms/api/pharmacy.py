"""Permission-checked choices for the prescription dispensing dialog."""
import frappe
from frappe import _
from frappe.utils import flt

from hms.workflows import PHARMACY_ROLES, checked_doc, require_roles


@frappe.whitelist()
def prescription_lines(visit):
	require_roles(PHARMACY_ROLES)
	doc = checked_doc("Patient Visit", visit)
	if doc.status not in ("Prescription Given", "Completed"):
		frappe.throw(_("Select a saved prescription before dispensing."))
	lines = []
	for row in doc.medication_schedule:
		item = frappe.db.get_value("Medicine", row.medicine, "med_item")
		used = frappe.db.sql(
			"""select coalesce(sum(case when m.transaction_type='Return' then -r.med_quantity else r.med_quantity end),0)
			from `tabOut Medical Item` r join `tabMeds Out` m on m.name=r.parent
			where m.patient_visit=%s and m.status='Posted' and r.prescription_row=%s and r.parenttype='Meds Out'""",
			(doc.name, row.name),
		)[0][0]
		remaining = flt(flt(row.quantity) - flt(used), 6)
		if item and remaining > 0:
			lines.append(
				{
					"name": row.name,
					"medicine": row.medicine,
					"dose": row.dose,
					"medical_item": item,
					"remaining": remaining,
				}
			)
	return {"patient": doc.patient, "lines": lines}
