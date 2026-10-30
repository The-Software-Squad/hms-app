"""Permission-scoped operational snapshots for the Hospital Live schematic."""
import frappe
from frappe import _
from frappe.utils import cint, getdate, now_datetime, nowdate

from hms.workflows import CLINICAL_ROLES, atomic_action, lock, require_roles

LIVE_ROLES = {"System Manager", "Receptionist", "Doctor", "Pharmacist"}
ACTIVE_VISITS = (
	"Checked In",
	"Under Consultation",
	"Lab/Diagnostics Pending",
	"Lab/Diagnostics Completed",
	"Prescription Given",
)
LIMIT = 1000


def visible(doctype, fields, filters=None, order_by="creation asc"):
	"""Never bypass record/user permission rules for this shared display."""
	if not frappe.has_permission(doctype, "read"):
		return [], False
	rows = frappe.get_list(
		doctype, filters=filters or {}, fields=fields, order_by=order_by, limit_page_length=LIMIT + 1
	)
	return rows[:LIMIT], len(rows) > LIMIT


@frappe.whitelist()
def snapshot():
	require_roles(LIVE_ROLES)
	today = nowdate()
	truncated = []

	def read(doctype, fields, filters=None, order_by="creation asc"):
		rows, more = visible(doctype, fields, filters, order_by)
		if more:
			truncated.append(doctype)
		return rows

	practitioners = read(
		"Healthcare Practitioner",
		["name", "practitioner_name", "department", "user", "presence_status", "presence_updated_on"],
		{"active": 1},
		"practitioner_name asc",
	)
	visits = read(
		"Patient Visit",
		["name", "patient", "doctor", "status", "visit_date", "creation", "modified"],
		{"visit_date": today, "status": ["in", ACTIVE_VISITS]},
	)
	older_visits = read(
		"Patient Visit",
		["name", "patient", "doctor", "status", "visit_date", "creation", "modified"],
		{"visit_date": ["<", today], "status": ["in", ACTIVE_VISITS]},
	)
	appointments = read(
		"Patient Appointment",
		["name", "practitioner", "start_time"],
		{"appointment_date": today, "status": "Scheduled"},
		"start_time asc",
	)
	admissions = read(
		"IP Record",
		["name", "patient", "bed", "practitioner", "status", "admission_date", "modified"],
		{"status": ["!=", "Discharged"]},
	)
	beds = read(
		"Bed", ["name", "bed_number", "ward", "current_admission"], order_by="ward asc, bed_number asc"
	)
	labs = read(
		"Lab Report", ["name", "visit_reference", "status"], {"status": ["in", ["Requested", "Received"]]}
	)
	sales = read(
		"Meds Out",
		[
			"name",
			"patient",
			"patient_visit",
			"customer_name",
			"collection_status",
			"collection_tracking",
			"date",
			"modified",
		],
		{
			"transaction_type": "Sale",
			"status": "Posted",
			"collection_tracking": 1,
			"collection_status": ["in", ["Not Collected", "Partly Collected"]],
		},
	)
	# Retrieve only permitted patient labels; never expose contact/clinical/financial content.
	patient_ids = sorted({r.patient for r in [*visits, *older_visits, *admissions, *sales] if r.patient})
	patients = read("Patient", ["name", "patient_name"], {"name": ["in", patient_ids]}) if patient_ids else []
	labels = {p.name: p.patient_name for p in patients}
	settings = frappe.get_single("Hospital Settings")
	configured = settings.get("simulation_rooms") or []
	room_by_doctor = {r.practitioner: r for r in configured if r.enabled}
	rooms = []
	for doctor in practitioners:
		if configured and doctor.name not in room_by_doctor:
			continue
		config = room_by_doctor.get(doctor.name)
		reported = doctor.presence_updated_on and getdate(doctor.presence_updated_on) == getdate(today)
		rooms.append(
			dict(
				id=doctor.name,
				doctor=doctor.practitioner_name,
				department=doctor.department or "Consultation",
				room_name=config.room_name if config else f"Consultation {len(rooms)+1:02d}",
				seats=cint(config.waiting_seats) if config else 8,
				availability=doctor.presence_status if reported else "Not Recorded",
				availability_updated_on=str(doctor.presence_updated_on) if reported else None,
				can_update_availability=frappe.session.user == "Administrator"
				or "System Manager" in frappe.get_roles()
				or ("Doctor" in frappe.get_roles() and doctor.user == frappe.session.user),
			)
		)
	if configured:
		order = {r.practitioner: i for i, r in enumerate(configured)}
		rooms.sort(key=lambda r: order[r["id"]])
	for row in [*visits, *older_visits, *admissions]:
		row.patient_label = labels.get(row.patient) or "Patient"
	for row in sales:
		row.patient_label = labels.get(row.patient) or row.customer_name or "Patient"
		row.pop("customer_name", None)
	return dict(
		as_of=str(now_datetime()),
		date=today,
		rooms=rooms,
		visits=visits,
		older_visits=older_visits,
		appointments=appointments,
		admissions=admissions,
		beds=beds,
		labs=labs,
		pharmacy=sales,
		truncated=truncated,
		access={
			dt: bool(frappe.has_permission(dt, "read"))
			for dt in ["Patient Visit", "Lab Report", "Meds Out", "IP Record", "Bed"]
		},
		can_configure="System Manager" in frappe.get_roles(),
	)


@frappe.whitelist(methods=["POST"])
@atomic_action
def set_availability(practitioner, status):
	require_roles(CLINICAL_ROLES)
	if status not in ("Available", "Away", "Off Duty"):
		frappe.throw(_("Choose Available, Away or Off Duty."))
	lock("Healthcare Practitioner", practitioner)
	doctor = frappe.get_doc("Healthcare Practitioner", practitioner, for_update=True)
	doctor.check_permission("read")
	if "System Manager" not in frappe.get_roles() and doctor.user != frappe.session.user:
		frappe.throw(_("You may only report your own availability."), frappe.PermissionError)
	if not doctor.active:
		frappe.throw(_("An inactive practitioner cannot report availability."))
	doctor.presence_status, doctor.presence_updated_on, doctor.presence_updated_by = (
		status,
		now_datetime(),
		frappe.session.user,
	)
	frappe.flags.hms_practitioner_presence = True
	try:
		doctor.save(ignore_permissions=True)
	finally:
		frappe.flags.hms_practitioner_presence = False
	return {"status": doctor.presence_status, "updated_on": str(doctor.presence_updated_on)}
