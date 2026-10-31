frappe.ui.form.on("IP Record", {
	refresh(frm) {
		if (
			!frm.is_new() &&
			!["Completed", "Cancelled / No Show", "Closed Early", "Discharged"].includes(
				frm.doc.status
			) &&
			frappe.model.can_create("HMS Patient Departure")
		) {
			frm.add_custom_button(
				__("Record Departure"),
				() =>
					frappe.new_doc("HMS Patient Departure", {
						source_doctype: frm.doctype,
						source_name: frm.doc.name,
					}),
				__("Create")
			);
		}

		if (frm.is_new()) return;
		if (frappe.model.can_read("In Patient Treatment"))
			frm.add_custom_button(
				__("Treatment History"),
				() =>
					frappe.set_route("List", "In Patient Treatment", { in_patient: frm.doc.name }),
				__("View")
			);
		if (frm.doc.status !== "Discharged") {
			if (frappe.model.can_create("In Patient Treatment"))
				frm.add_custom_button(
					__("Record Treatment"),
					() =>
						frappe.new_doc("In Patient Treatment", {
							in_patient: frm.doc.name,
							patient: frm.doc.patient,
							practitioner: frm.doc.practitioner,
						}),
					__("Create")
				);
			if (frappe.model.can_create("Discharge Summary"))
				frm.add_custom_button(
					__("Discharge Summary"),
					() =>
						frappe.new_doc("Discharge Summary", {
							in_patient: frm.doc.name,
							patient: frm.doc.patient,
							practitioner: frm.doc.practitioner,
						}),
					__("Create")
				);
		} else if (frappe.user_roles.some((role) => ["Doctor", "System Manager"].includes(role))) {
			frm.add_custom_button(
				__("Reopen Admission"),
				() =>
					frappe.prompt(
						{
							fieldname: "reason",
							fieldtype: "Small Text",
							label: __("Reopening reason"),
							reqd: 1,
						},
						(values) => frm.call("reopen", values).then(() => frm.reload_doc())
					),
				__("Actions")
			);
		}
	},
});
