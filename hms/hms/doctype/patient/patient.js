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

		// Update age display if DOB present
		update_age_html(frm);

		// Address & Contact UI
		frm.toggle_display(['address_html', 'contact_html', 'address_contacts'], !frm.is_new());
		if (frm.is_new()) {
			frappe.contacts && frappe.contacts.clear_address_and_contact(frm);
		} else {
			frappe.contacts && frappe.contacts.render_address_and_contact(frm);
		}
	},
	refresh(frm) {
        if (!frm.doc.__islocal) {
            add_new_patient_visit_button(frm);
            render_previous_visits_table(frm);
        }

		// Keep age HTML in sync
		update_age_html(frm);

		// Address & Contact UI
		frm.toggle_display(['address_html', 'contact_html', 'address_contacts'], !frm.is_new());
		if (frm.is_new()) {
			frappe.contacts && frappe.contacts.clear_address_and_contact(frm);
		} else {
			frappe.contacts && frappe.contacts.render_address_and_contact(frm);
		}
	},
	dob(frm) {
		update_age_html(frm);
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
    const calls = [
        {
            method: "hms.api.patient.get_latest_follow_up",
            fieldname: "follow_up"
        },
        {
            method: "hms.api.patient.get_latest_validity_expiry",
            fieldname: "validity_expiring_on"
        }
    ];

    calls.forEach((c) => {
        frappe.call({
            method: c.method,
            args: { patient: frm.doc.name },
            callback: (r) => {
                const new_value = r.message;
                const current_value = frm.doc[c.fieldname];
                if (new_value && new_value !== current_value) {
                    frm.set_value(c.fieldname, new_value);
                    frm.save();
                }
            }
        });
    });
}

function add_new_patient_visit_button(frm) {
    frm.add_custom_button("New Patient Visit", () => {
        frappe.route_options = { patient: frm.doc.name };
        frappe.set_route("Form", "Patient Visit", "new-patient-visit");
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

// Removed Out Patient child table handlers as Fee Validity supersedes OP

function update_age_html(frm) {
	const dob = frm.doc.dob;
	const target = frm.fields_dict.age_html?.$wrapper;
	if (!target) return;

	if (!dob) {
		target.html('<span class="text-muted">—</span>');
		return;
	}

	try {
		const birth = frappe.datetime.str_to_obj(dob);
		const today = new Date();
		let years = today.getFullYear() - birth.getFullYear();
		let months = today.getMonth() - birth.getMonth();
		let days = today.getDate() - birth.getDate();

		if (days < 0) {
			months -= 1;
			days += new Date(today.getFullYear(), today.getMonth(), 0).getDate();
		}
		if (months < 0) {
			years -= 1;
			months += 12;
		}

		const parts = [];
		if (years > 0) parts.push(`${years}y`);
		if (months > 0) parts.push(`${months}m`);
		if (years <= 0 && months <= 0) parts.push(`${days}d`);

		target.html(`<span>${parts.join(' ')}</span>`);
	} catch (e) {
		target.html('<span class="text-muted">—</span>');
	}
}
