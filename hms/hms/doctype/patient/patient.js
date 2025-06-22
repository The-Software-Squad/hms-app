// Copyright (c) 2024, nani-samireddy and contributors
// For license information, please see license.txt
frappe.ui.form.on("Patient", {
	refresh(frm) {
		if (!frm.doc.__islocal) {
			// ---------- New Patient Visit or OP Record Button ----------
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "OP Record",
					filters: {
						patient: frm.doc.name,
						status: "Open",
						valid_till: [">=", frappe.datetime.now_date()]
					},
					limit: 1,
					order_by: "valid_till desc"
				},
				callback(r) {
					const existing_op = r.message?.[0];

					if (existing_op) {
						frm.add_custom_button("New Patient Visit", () => {
							frappe.route_options = {
								patient: frm.doc.name,
								op_record: existing_op.name
							};
							frappe.set_route("Form", "Patient Visit", "new-patient-visit");
						});
					} else {
						frm.add_custom_button("New OP Record", () => {
							frappe.route_options = {
								patient: frm.doc.name
							};
							frappe.set_route("Form", "OP Record", "new-op-record");
						});
					}
				}
			});

			// ---------- Latest OP Record Button ----------
			frappe.call({
				method: "hms.api.patient.get_latest_op_expiry",
				args: {
					patient: frm.doc.name
				},
				callback: (r) => {
					if (r.message) {
						frm.set_value("latest_op_expires_on", r.message);
					}
				}
			});

			// ---------- Follow-Up Button ----------
			frappe.call({
				method: "hms.api.patient.get_latest_follow_up",
				args: {
					patient: frm.doc.name
				},
				callback: (r) => {
					if (r.message) {
						frm.set_value("follow_up", r.message);
					}
				}
			});
		}

		// ---------- "View" Section ----------
		frm.add_custom_button("📄 OP Records", () => {
			frappe.set_route("List", "OP Record", {
				patient: frm.doc.name
			});
		}, "View");

		frm.add_custom_button("📋 Visit History", () => {
			frappe.set_route("List", "Patient Visit", {
				patient: frm.doc.name
			});
		}, "View");

		frm.add_custom_button("🧪 Lab Reports", () => {
			frappe.set_route("List", "Lab Report", {
				patient: frm.doc.name
			});
		}, "View");
	},
});
