frappe.query_reports["HMS Reconciliation"] = {
	filters: [
		{ fieldname: "patient", label: __("Patient"), fieldtype: "Link", options: "Patient" },
		{
			fieldname: "outstanding_only",
			label: __("Outstanding only"),
			fieldtype: "Check",
			default: 0,
		},
	],
};
