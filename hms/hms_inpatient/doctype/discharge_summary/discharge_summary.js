frappe.ui.form.on("Discharge Summary", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Finalize Discharge"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save the summary first."));
				frappe.confirm(
					__("Finalize this summary, discharge the patient and release the bed?"),
					() => frm.call("finalize").then(() => frm.reload_doc())
				);
			});
	},
});
