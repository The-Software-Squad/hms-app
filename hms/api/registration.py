import frappe
from frappe import _
from frappe.utils import getdate, now_datetime

from hms.workflows import atomic_action, checked_doc, lock, require_roles, update_patient_dates


@frappe.whitelist(methods=["POST"])
@atomic_action
def merge_patients(source, target, reason):
	"""An explicit administrator action, never automatic name/phone-based merging."""
	require_roles({"System Manager"})
	if source == target or not reason or not reason.strip():
		frappe.throw(_("Choose two different patients and provide a merge reason."))
	for name in sorted((source, target)):
		checked_doc("Patient", name, "write")
		lock("Patient", name)
	a, b = frappe.get_doc("Patient", source), frappe.get_doc("Patient", target)
	if (a.uid and b.uid and a.uid != b.uid) or (a.dob and b.dob and getdate(a.dob) != getdate(b.dob)):
		frappe.throw(_("Conflicting patient identifiers or dates of birth must be resolved before merging."))
	if (
		frappe.db.count("IP Record", {"patient": ["in", [source, target]], "status": ["!=", "Discharged"]})
		> 1
	):
		frappe.throw(_("Resolve the conflicting active admissions before merging patients."))
	for doctype in ("HMS Invoice", "Payment Recipit"):
		if frappe.db.exists(doctype, {"patient": source}):
			frappe.throw(
				_(
					"The source patient has financial records. Reconcile billing identity with an administrator before merging."
				)
			)
	frappe.get_doc(
		{
			"doctype": "HMS Patient Merge",
			"source_patient": source,
			"target_patient": target,
			"reason": reason.strip(),
			"performed_by": frappe.session.user,
			"performed_on": now_datetime(),
			"source_snapshot": frappe.as_json(a.as_dict()),
		}
	).insert(ignore_permissions=True)
	frappe.rename_doc("Patient", source, target, merge=True, force=True)
	# Linked child records and beds are renamed by Frappe; keep denormalized contact/dates consistent.
	frappe.get_doc("Patient", target).set_contact()
	update_patient_dates(target)
	return {"patient": target}
