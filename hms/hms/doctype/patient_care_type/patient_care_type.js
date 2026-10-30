frappe.ui.form.on("Patient Care Type", {
	refresh(frm) {
		frm.set_intro(
			__(
				"This legacy master is retained for compatibility. Use the clinical and inpatient workflows for current workflows."
			),
			"orange"
		);
	},
});
