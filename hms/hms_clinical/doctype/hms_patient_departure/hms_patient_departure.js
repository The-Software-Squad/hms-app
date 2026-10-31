frappe.ui.form.on("HMS Patient Departure", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.status === "Draft")
			frm.add_custom_button(__("Finalize Departure"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes first."));
				frm.call("finalize").then(() => frm.reload_doc());
			});
		if (
			frm.doc.review_status === "Pending" &&
			frappe.user_roles.some((r) => ["Doctor", "System Manager"].includes(r))
		) {
			frm.set_intro(
				__(
					"The patient has left. Pending results still require clinical review by the assigned practitioner."
				),
				"orange"
			);
			frm.add_custom_button(__("Resolve Results Review"), () =>
				frm.call("resolve_review").then(() => frm.reload_doc())
			);
		}
	},
});
