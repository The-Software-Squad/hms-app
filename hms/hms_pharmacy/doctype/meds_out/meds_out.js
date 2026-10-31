frappe.ui.form.on("Meds Out", {
	setup(frm) {
		frm.set_query("stock_lot", "details", () => ({
			filters:
				frm.doc.transaction_type === "Sale"
					? {
							available_quantity: [">", 0],
							expires_at: [">=", frappe.datetime.get_today()],
					  }
					: {},
			order_by: "expires_at asc",
		}));
	},
	refresh(frm) {
		frm.page.set_title(__("Dispensing"));
		frm.page.set_title_sub(frm.is_new() ? __("New") : frm.doc.name);
		if (
			frm.doc.status === "Posted" &&
			frm.doc.transaction_type === "Sale" &&
			frm.doc.collection_tracking &&
			frappe.model.can_create("HMS Pharmacy Collection")
		) {
			frm.add_custom_button(__("Record Handover"), async () => {
				const { message: details } = await frm.call("collection_items");
				if (!details.length)
					return frappe.msgprint(__("No medicines remain to hand over."));
				frappe.new_doc("HMS Pharmacy Collection", { source_sale: frm.doc.name, details });
			});
		}
		if (
			frm.doc.status === "Posted" &&
			frm.doc.transaction_type === "Sale" &&
			!frm.doc.collection_tracking
		)
			frm.set_intro(
				__(
					"Historical collection was not tracked. Do not infer whether these medicines were handed over."
				),
				"orange"
			);
		if (
			frm.doc.status === "Draft" &&
			frm.doc.transaction_type === "Sale" &&
			frm.doc.patient_visit
		)
			frm.add_custom_button(__("Add From Prescription"), () => add_prescription_item(frm));
		if (!frm.is_new() && frm.doc.status === "Draft")
			frm.add_custom_button(__("Post Dispensing"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save changes before posting."));
				frappe.confirm(
					__("Post Dispensing? Posted records require a reversal to correct."),
					() => frm.call("post").then(() => frm.reload_doc())
				);
			});
		if (frm.doc.status === "Posted" && frm.doc.transaction_type === "Sale")
			frm.add_custom_button(__("Record Return"), () =>
				frappe.new_doc("Meds Out", {
					transaction_type: "Return",
					return_against: frm.doc.name,
					patient: frm.doc.patient,
					meds_out_type: frm.doc.meds_out_type,
					customer_name: frm.doc.customer_name,
					patient_visit: frm.doc.patient_visit,
					currency: frm.doc.currency,
					details: frm.doc.details.map((r) => ({
						stock_lot: r.stock_lot,
						med_quantity: r.med_quantity,
						med_price: r.med_price,
						prescription_row: r.prescription_row,
					})),
				})
			);
	},
});

async function add_prescription_item(frm) {
	const { message } = await frappe.call({
		method: "hms.api.pharmacy.prescription_lines",
		args: { visit: frm.doc.patient_visit },
	});
	if (message.patient !== frm.doc.patient)
		return frappe.msgprint(__("Select the patient belonging to this prescription."));
	if (!message.lines.length)
		return frappe.msgprint(
			__("No remaining approved quantities with pharmacy item mappings.")
		);
	const choices = message.lines.map(
		(line, index) =>
			`${index + 1}. ${line.medicine} · ${line.dose} · ${__("Remaining")}: ${line.remaining}`
	);
	let dialog;
	const line = () => message.lines[choices.indexOf(dialog?.get_value("prescription"))];
	dialog = new frappe.ui.Dialog({
		title: __("Add Prescription Item"),
		fields: [
			{
				fieldname: "prescription",
				fieldtype: "Select",
				label: __("Prescription"),
				options: choices,
				default: choices[0],
				reqd: 1,
				onchange: () => {
					const selected = line();
					if (selected) {
						dialog.set_value("quantity", selected.remaining);
						dialog.set_value("stock_lot", "");
					}
				},
			},
			{
				fieldname: "stock_lot",
				fieldtype: "Link",
				options: "HMS Stock Lot",
				label: __("Stock Lot"),
				reqd: 1,
				get_query: () => ({
					filters: {
						medical_item: line()?.medical_item,
						available_quantity: [">", 0],
						expires_at: [">=", frappe.datetime.get_today()],
					},
					order_by: "expires_at asc",
				}),
			},
			{
				fieldname: "quantity",
				fieldtype: "Float",
				label: __("Quantity"),
				default: message.lines[0].remaining,
				reqd: 1,
			},
			{
				fieldname: "rate",
				fieldtype: "Currency",
				label: __("Selling Unit Price"),
				default: 0,
				description: __("Enter the price charged to the patient."),
			},
		],
		primary_action_label: __("Add Item"),
		primary_action: (values) => {
			const selected = line();
			if (values.quantity <= 0 || values.quantity > selected.remaining || values.rate < 0)
				return frappe.msgprint(
					__(
						"Enter a positive quantity within the prescription limit and a non-negative price."
					)
				);
			if ((frm.doc.details || []).some((row) => row.stock_lot === values.stock_lot))
				return frappe.msgprint(
					__("This lot is already present. Update its existing quantity.")
				);
			frm.doc.details = (frm.doc.details || []).filter(
				(row) => row.stock_lot || row.med_quantity || row.med_price
			);
			frm.add_child("details", {
				medical_item: selected.medical_item,
				stock_lot: values.stock_lot,
				prescription_row: selected.name,
				med_quantity: values.quantity,
				med_price: values.rate,
			});
			frm.refresh_field("details");
			dialog.hide();
		},
	});
	dialog.show();
}
