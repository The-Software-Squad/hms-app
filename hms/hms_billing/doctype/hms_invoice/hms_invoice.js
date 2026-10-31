frappe.ui.form.on("HMS Invoice", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Issue Invoice"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes before posting."));
				frappe.confirm(
					__("Issue Invoice? Posted records require a reversal to correct."),
					() => frm.call("issue").then(() => frm.reload_doc())
				);
			});
		if (
			!["Draft", "Void"].includes(frm.doc.status) &&
			frm.doc.invoice_type === "Invoice" &&
			frm.doc.outstanding_amount > 0
		)
			frm.add_custom_button(__("Record Payment"), () =>
				frappe.new_doc("Payment Recipit", {
					patient: frm.doc.patient,
					paid_by: frm.doc.payer_name,
					currency: frm.doc.currency,
					amount: frm.doc.outstanding_amount,
					payment_date: frappe.datetime.get_today(),
					towards: __("Invoice {0}", [frm.doc.name]),
					allocations: [{ invoice: frm.doc.name, amount: frm.doc.outstanding_amount }],
				})
			);
		if (
			!["Draft", "Void"].includes(frm.doc.status) &&
			frm.doc.invoice_type === "Invoice" &&
			frm.doc.total > frm.doc.credited_amount
		)
			frm.add_custom_button(__("Create Credit"), () =>
				frappe.new_doc("HMS Invoice", {
					invoice_type: "Credit",
					credit_against: frm.doc.name,
					patient: frm.doc.patient,
					payer_name: frm.doc.payer_name,
					currency: frm.doc.currency,
					items: [
						{
							description: __("Credit for {0}", [frm.doc.name]),
							quantity: 1,
							rate: frm.doc.total - frm.doc.credited_amount,
						},
					],
				})
			);
		if (
			!frm.is_new() &&
			!frm.doc.source_key &&
			!["Draft", "Void"].includes(frm.doc.status) &&
			!frm.doc.paid_amount &&
			!frm.doc.credited_amount &&
			frm.doc.invoice_type === "Invoice"
		)
			frm.add_custom_button(__("Void Invoice"), () =>
				frappe.prompt(
					{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 },
					({ reason }) => frm.call("void", { reason }).then(() => frm.reload_doc())
				)
			);
	},
});
