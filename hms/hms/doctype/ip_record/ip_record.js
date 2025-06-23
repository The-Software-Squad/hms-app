// Copyright (c) 2025, nani-samireddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("IP Record", {
	refresh(frm) {
		// Check if the form is not new
		if (frm.is_new()) return;
		console.log("IP Record Form Loaded");
		// Add view buttons.
		add_view_buttons(frm);
	},
});

function add_view_buttons(frm) {
	const view_buttons = [
		{
			label: "Treatment History",
			doctype: "In Patient Treatment",
		}
	];

	view_buttons.forEach(button => {
		frm.add_custom_button(button.label, () => {
			frappe.set_route("List", button.doctype, {
				in_patient: frm.doc.name
			});
		}, "View");
	});
}