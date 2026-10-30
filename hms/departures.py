"""Guard the server-owned disposition separately from clinical and financial progress."""
import frappe
from frappe import _

DEPARTURE_FIELDS = ("departure_record", "departure_outcome", "departed_on")


def validate_departure_fields(doc):
	old = doc.get_doc_before_save()
	changed = any(str(doc.get(k) or "") != str(old.get(k) or "" if old else "") for k in DEPARTURE_FIELDS)
	if changed and not (frappe.flags.hms_departure or frappe.flags.hms_reopen):
		frappe.throw(_("Use Record Departure to record the patient's departure."))
