frappe.ui.form.on("Medical Department", {
	refresh(frm) {
		frm.set_intro(
			__(
				"This legacy master is retained for compatibility. Use Departments (Department Type) for current workflows."
			),
			"orange"
		);
	},
});
