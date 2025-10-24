// Copyright (c) 2024, nani-samireddy and contributors
// For license information, please see license.txt
frappe.ui.form.on("Patient", {
	onload_post_render(frm) {
		if (!frm.doc.__islocal) {
			// Show IP Records Button
			add_ip_record_button(frm);
			// ---------- Fetch and Update Fields ----------
			fetch_and_update_fields(frm);
			// Conditionally show New Patient Visit if active Out Patient exists
			add_new_patient_visit_button_if_active_op(frm);
			// Render patient history table in HTML field
			render_previous_visits_table(frm);
		}

		// Add view buttons for Visit History, Lab Reports, and IP Records
		add_view_buttons(frm);
	},
	refresh(frm) {
		if (!frm.doc.__islocal) {
			add_new_patient_visit_button_if_active_op(frm);
			render_previous_visits_table(frm);
		}
	}
});

function add_view_buttons(frm) {
	const view_buttons = [
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
				const new_value = r.message;
				const current_value = frm.doc[endpoint.fieldname];
				
				if (new_value && new_value !== current_value) {
					frm.set_value(endpoint.fieldname, new_value);
					
					// save the form after updating fields
					frm.save();
				}
			}
		});
	});

}

function add_new_patient_visit_button_if_active_op(frm) {
	frappe.call({
		method: "hms.api.patient.has_active_out_patient",
		args: { patient: frm.doc.name },
		callback: (r) => {
			if (r.message) {
				frm.add_custom_button("New Patient Visit", () => {
					frappe.route_options = { patient: frm.doc.name };
					frappe.set_route("Form", "Patient Visit", "new-patient-visit");
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
						in_patient: existing_op.name
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

function render_previous_visits_table(frm) {
	const wrapper = frm.fields_dict.previous_visits?.$wrapper;
	if (!wrapper) return;

	// Basic table skeleton
	wrapper.html(`
		<div class="patient-history">
			<table class="table table-bordered" style="width: 100%;">
				<thead>
					<tr>
						<th style="white-space: nowrap;">Visit Date</th>
						<th>Department</th>
						<th>Doctor</th>
						<th style="white-space: nowrap;">Follow Up</th>
						<th style="width: 1%; white-space: nowrap;">Action</th>
					</tr>
				</thead>
				<tbody id="prev-visits-body">
					<tr><td colspan="5" class="text-muted">Loading...</td></tr>
				</tbody>
			</table>
		</div>
	`);

	frappe.call({
		method: 'hms.api.patient.get_previous_patient_visits',
		args: {
			patient: frm.doc.name,
			limit: 50,
			offset: 0
		},
		callback: (r) => {
			const body = wrapper.find('#prev-visits-body');
			body.empty();
			const visits = r.message || [];
			if (!visits.length) {
				body.append('<tr><td colspan="5" class="text-muted">No previous visits found</td></tr>');
				return;
			}

			visits.forEach(v => {
				const visitDate = v.visit_date ? frappe.datetime.str_to_user(v.visit_date) : '—';
				const followUp = v.follow_up ? frappe.datetime.str_to_user(v.follow_up) : '—';
				const dept = v.department ? frappe.utils.escape_html(v.department) : '—';
				const doctor = v.doctor_name ? frappe.utils.escape_html(v.doctor_name) : (v.doctor ? frappe.utils.escape_html(v.doctor) : '—');
				const link = `/app/patient-visit/${v.name}`;
				body.append(`
					<tr>
						<td>${visitDate}</td>
						<td>${dept}</td>
						<td>${doctor}</td>
						<td>${followUp}</td>
						<td><a class="btn btn-sm btn-secondary" href="${link}" target="_blank">Open</a></td>
					</tr>
				`);
			});
		}
	});
}

frappe.ui.form.on('Out Patient', {
	op_records_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Get the current date.
		let current_date = frappe.datetime.nowdate();
		
		// Check for overlapping dates
		if (isDateOverlapping(frm, cdt, cdn, current_date)) {
			return;
		}

		// Set the 'from' date to the current date if it's empty
		if (!row.from) {
			frappe.model.set_value(cdt, cdn, 'from', current_date);
		}

		if (row.from && !row.to) {  // Only if 'to' is empty
			let to_date = frappe.datetime.add_days(row.from, 30);
			frappe.model.set_value(cdt, cdn, 'to', to_date);
		}
	},

	from(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Check for overlapping dates
		if (isDateOverlapping(frm, cdt, cdn, row.from)) {
			frappe.model.set_value(cdt, cdn, 'from', null);
			frappe.msgprint(__('The selected "From" date overlaps with an existing Out Patient record. Please choose a different date.'));
			return;
		}

		if (row.from) {  // Only if 'to' is empty
			let to_date = frappe.datetime.add_days(row.from, 30);
			frappe.model.set_value(cdt, cdn, 'to', to_date);
		}
	},
});

function isDateOverlapping(frm, cdt, cdn, selectedDate) {
	let isOverlapping = false;
	frm.doc.op_records.forEach(record => {
		if (record.name !== cdn) { // Exclude the current record being edited
			let recordFrom = record.from;
			let recordTo = record.to || frappe.datetime.add_days(record.from, 30); // Default to 30 days if 'to' is not set

			if (selectedDate >= recordFrom && selectedDate <= recordTo) {
				isOverlapping = true;
			}
		}
	});
	return isOverlapping;
}
