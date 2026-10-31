frappe.ui.form.on("HMS Pharmacy Collection", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Post Handover"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes first."));
				frm.call("post").then(() => frm.reload_doc());
			});
	},
});
