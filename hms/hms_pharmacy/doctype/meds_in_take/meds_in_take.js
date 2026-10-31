frappe.ui.form.on("Meds In take", {
	refresh(frm) {
		frm.page.set_title(__("Stock intake"));
		frm.page.set_title_sub(frm.is_new() ? __("New") : frm.doc.name);
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Post Intake"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes before posting."));
				frappe.confirm(
					__("Post Intake? Posted records require a reversal to correct."),
					() => frm.call("post").then(() => frm.reload_doc())
				);
			});
		if (frm.doc.status === "Posted")
			frm.add_custom_button(__("Cancel Intake"), () =>
				frappe.prompt(
					{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 },
					(values) => frm.call("cancel_intake", values).then(() => frm.reload_doc())
				)
			);
	},
});
