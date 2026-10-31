frappe.ui.form.on("HMS Medication Delivery", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Refresh Delivery Status"), () =>
			frm.call("refresh_status").then(() => frm.reload_doc())
		);
		if (frm.doc.status === "Failed")
			frm.add_custom_button(__("Retry Failed Email"), () =>
				frappe.confirm(__("Retry the same saved prescription and recipient?"), () =>
					frm.call("retry").then(() => frm.reload_doc())
				)
			);
	},
});
