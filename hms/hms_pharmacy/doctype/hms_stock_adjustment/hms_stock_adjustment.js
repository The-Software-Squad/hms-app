frappe.ui.form.on("HMS Stock Adjustment", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Post Adjustment"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes before posting."));
				frappe.confirm(
					__("Post Adjustment? Posted records require a reversal to correct."),
					() => frm.call("post").then(() => frm.reload_doc())
				);
			});
	},
});
