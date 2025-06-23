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
			// Show OP Records Button and IP Records Button
			add_op_record_button(frm);
			add_ip_record_button(frm);
			// ---------- Fetch and Update Fields ----------
			fetch_and_update_fields(frm);
		}

		// Add view buttons for OP Records, Visit History, and Lab Reports
		add_view_buttons(frm);
	},
});

function add_view_buttons(frm) {
	const view_buttons = [
		{
			label: "📄 OP Records",
			doctype: "OP Record",
		},
		{
			label: "📋 Visit History",
			doctype: "Patient Visit",
		},
		{
			label: "🧪 Lab Reports",
			doctype: "Lab Report",
		},
		{
			label: "🩺 IP Records",
			doctype: "IP Record",
		},
		{
			label: "Treatment History",
			doctype: "In Patient Treatment",
		}
	];

	view_buttons.forEach(button => {
		frm.add_custom_button(button.label, () => {
			frappe.set_route("List", button.doctype, {
				patient: frm.doc.name
			});
		}, "View");
	});
}

function fetch_and_update_fields(frm) {
	const api_endpoints = [
		{
			method: "hms.api.patient.get_latest_op_expiry",
			fieldname: "latest_op_expires_on"
		},
		{
			method: "hms.api.patient.get_latest_follow_up",
			fieldname: "follow_up"
		}
	];

	api_endpoints.forEach(endpoint => {
		frappe.call({
			method: endpoint.method,
			args: {
				patient: frm.doc.name
			},
			callback: (r) => {
				if (r.message) {
					frm.set_value(endpoint.fieldname, r.message);
				}
			}
		});
	});
}

function add_op_record_button(frm) {
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
}

function add_ip_record_button(frm) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "IP Record",
			filters: {
				patient: frm.doc.name,
				status: ["!=", "Discharged"],
			},
			limit: 1,
			order_by: "admission_date desc"
		},
		callback(r) {
			const existing_op = r.message?.[0];

			if (existing_op) {
				frm.add_custom_button("New In Patient Treatment", () => {
					frappe.route_options = {
						patient: frm.doc.name,
						op_record: existing_op.name
					};
					frappe.set_route("Form", "In Patient Treatment", "new-in-patient-treatment");
				});
			} else {
				frm.add_custom_button("New IP Record", () => {
					frappe.route_options = {
						patient: frm.doc.name
					};
					frappe.set_route("Form", "IP Record", "new-ip-record");
				});
			}
		}
	});
}