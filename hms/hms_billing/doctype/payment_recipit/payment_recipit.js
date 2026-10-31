frappe.ui.form.on("Payment Recipit", {
	refresh(frm) {
		frm.page.set_title(__("Payment receipt"));
		frm.page.set_title_sub(frm.is_new() ? __("New") : frm.doc.name);
		if (!frm.is_new() && ["Draft", "Legacy Recorded"].includes(frm.doc.status))
			frm.add_custom_button(__("Post Payment"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes before posting."));
				frappe.confirm(
					__("Post Payment? Posted records require a reversal to correct."),
					() => frm.call("post").then(() => frm.reload_doc())
				);
			});
		if (frm.doc.status === "Posted" && frm.doc.transaction_type === "Receive")
			frm.add_custom_button(__("Record Refund"), () =>
				frappe.new_doc("Payment Recipit", {
					transaction_type: "Refund",
					reference_receipt: frm.doc.name,
					patient: frm.doc.patient,
					paid_by: frm.doc.paid_by,
					payment_mode: frm.doc.payment_mode,
					currency: frm.doc.currency,
					amount: frm.doc.amount,
					payment_date: frappe.datetime.get_today(),
					towards: __("Refund for {0}", [frm.doc.name]),
					allocations: frm.doc.allocations.map((r) => ({
						invoice: r.invoice,
						amount: r.amount,
					})),
				})
			);
	},
});
