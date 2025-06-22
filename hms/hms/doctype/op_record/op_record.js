// Copyright (c) 2025, nani-samireddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("OP Record", {
	refresh(frm) {
		if (!frm.doc.__islocal && frm.doc.patient) {
			// Show button to create new Patient Visit if the vaild_till date equal or greater than today
			if (frm.doc.valid_till && frappe.datetime.get_today() <= frm.doc.valid_till && frm.doc.status === "Open") {
				frm.add_custom_button("New Patient Visit", () => {
					frappe.route_options = {
						patient: frm.doc.patient,
						op_record: frm.doc.name
					};
					frappe.set_route("Form", "Patient Visit", "new-patient-visit");
				});
			}
			// Show button to view existing Patient Visits
			frm.add_custom_button("View Patient Visits", () => {
				frappe.set_route("List", "Patient Visit", {
					patient: frm.doc.patient,
					op_record: frm.doc.name
				});
			});
		}
	},
});
