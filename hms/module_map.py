"""Ownership of HMS records and navigation; HMS remains the shared core module."""

MODULES = ("HMS", "HMS Reception", "HMS Clinical", "HMS Inpatient", "HMS Pharmacy", "HMS Billing")

DOCTYPE_GROUPS = {
	"HMS": (
		"Patient",
		"HMS Patient Merge",
		"Hospital Settings",
		"HMS Simulation Room",
		"Employee",
		"Employee Role Type",
		"Healthcare Practitioner",
		"Department Type",
		"Medical Department",
		"Patient Care Type",
	),
	"HMS Reception": (
		"Patient Appointment",
		"Practitioner Schedule",
		"Practitioner Schedule Time Slot",
		"Fee Validity",
		"Fee Validity Reference",
	),
	"HMS Clinical": (
		"Patient Visit",
		"Medication Schedule",
		"Lab Report",
		"Lab Report Type",
		"HMS Medication Delivery",
		"HMS Patient Departure",
	),
	"HMS Inpatient": (
		"IP Record",
		"In Patient Treatment",
		"Vitals Entry",
		"Discharge Summary",
		"Ward",
		"Ward Type",
		"Bed",
	),
	"HMS Pharmacy": (
		"Medicine",
		"Medicine Timing",
		"Timing",
		"Med Item",
		"Meds Provider",
		"Meds In take",
		"Intake Medical Item",
		"Meds Out",
		"Out Medical Item",
		"HMS Stock Lot",
		"HMS Stock Movement",
		"HMS Stock Adjustment",
		"HMS Pharmacy Collection",
		"HMS Pharmacy Collection Item",
	),
	"HMS Billing": (
		"HMS Invoice",
		"HMS Invoice Item",
		"Payment Recipit",
		"HMS Payment Allocation",
		"Payment Purpose",
		"Payment Purpose Detail",
	),
}

ENTITY_MODULES = {
	"DocType": {name: module for module, names in DOCTYPE_GROUPS.items() for name in names},
	"Workspace": {
		"My Dashboard": "HMS",
		"Analytics": "HMS",
		"Reception Dashboard": "HMS Reception",
		"Doctor Dashboard": "HMS Clinical",
		"Follow-ups": "HMS Clinical",
		"Pharmacist Dashboard": "HMS Pharmacy",
		"Accounts": "HMS Billing",
	},
	"Page": {"hms-guide": "HMS", "hospital-live": "HMS"},
	"Report": {"HMS Reconciliation": "HMS Billing"},
	"Dashboard Chart": {
		"By Purpose": "HMS Billing",
		"Payment Mode": "HMS Billing",
		"Total Collection": "HMS Billing",
	},
	"Number Card": {
		"New Patients Today": "HMS Reception",
		"Total Collection": "HMS Billing",
		"Total In Patients": "HMS Inpatient",
		"Total Patient vists": "HMS Clinical",
		"Total Patients Visits": "HMS Clinical",
	},
}
