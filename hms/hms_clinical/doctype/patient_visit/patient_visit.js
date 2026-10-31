frappe.ui.form.on("Patient Visit", {
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
		if (frm.doc.follow_up && frappe.model.can_create("Patient Appointment"))
			frm.add_custom_button(
				__("Book Follow-up"),
				() =>
					frappe.new_doc("Patient Appointment", {
						patient: frm.doc.patient,
						practitioner: frm.doc.doctor,
						department: frm.doc.department,
						appointment_date: frm.doc.follow_up,
						follow_up_visit: frm.doc.name,
					}),
				__("Create")
			);
		const clinical = frappe.user_roles.some((role) =>
			["Doctor", "System Manager"].includes(role)
		);
		if (
			clinical &&
			!["Completed", "Closed Early", "Cancelled / No Show"].includes(frm.doc.status)
		) {
			frm.add_custom_button(
				__("Request Lab Report"),
				() =>
					frappe.new_doc("Lab Report", {
						visit_reference: frm.doc.name,
						patient: frm.doc.patient,
						requested_on: frappe.datetime.get_today(),
					}),
				__("Create")
			);
		}
		if (clinical) {
			frm.add_custom_button(
				__("Preview Medication Calendar"),
				async () => {
					const { message } = await frappe.call({
						method: "hms.api.mailer.preview_medication_calendar",
						args: { visit: frm.doc.name },
					});
					const dialog = new frappe.ui.Dialog({
						title: __("Medication Calendar Preview"),
						fields: [
							{
								fieldname: "calendar",
								fieldtype: "Code",
								options: "Text",
								label: __("Saved medication schedule"),
								read_only: 1,
							},
						],
					});
					dialog.set_value("calendar", message);
					dialog.show();
				},
				__("Medication")
			);
			frm.add_custom_button(
				__("Send Medication Mail"),
				() => {
					if (frm.is_dirty()) return frappe.msgprint(__("Save changes before sending."));
					frappe.confirm(
						__("Queue the saved medication schedule to the patient's email?"),
						() =>
							frappe.call({
								method: "hms.api.mailer.send_medication_mail",
								type: "POST",
								args: { visit: frm.doc.name },
								freeze: true,
								callback: (r) => {
									frappe.msgprint(
										r.message.duplicate
											? __(
													"This prescription is already queued or sent. See its delivery record."
											  )
											: __(
													"Medication email queued. Check delivery status for confirmation."
											  )
									);
									frappe.set_route(
										"Form",
										"HMS Medication Delivery",
										r.message.delivery
									);
								},
							})
					);
				},
				__("Medication")
			);
			render_visit_history(frm);
		}
		if (frm.doc.invoice && frappe.model.can_read("HMS Invoice"))
			frm.add_custom_button(
				__("Invoice"),
				() => frappe.set_route("Form", "HMS Invoice", frm.doc.invoice),
				__("View")
			);
		if (frappe.model.can_create("Meds Out"))
			frm.add_custom_button(
				__("Dispense Prescription"),
				() =>
					frappe.new_doc("Meds Out", {
						patient: frm.doc.patient,
						patient_visit: frm.doc.name,
					}),
				__("Create")
			);
	},
});

function render_visit_history(frm) {
	const wrapper = frm.fields_dict.previous_visits?.$wrapper;
	if (!wrapper) return;
	wrapper.empty();
	const list = $("<div>").appendTo(wrapper);
	const more = $("<button type='button' class='btn btn-default btn-sm'>")
		.text(__("Load previous visits"))
		.appendTo(wrapper);
	let offset = 0;
	more.on("click", async () => {
		more.prop("disabled", true);
		try {
			const { message: rows } = await frappe.call({
				method: "hms.api.patient.get_previous_patient_visits",
				args: { patient: frm.doc.patient, exclude_visit: frm.doc.name, limit: 10, offset },
			});
			(rows || []).forEach((visit) => {
				const card = $("<div class='border rounded p-3 mb-3'>").appendTo(list);
				$("<a>")
					.attr("href", `/desk/patient-visit/${encodeURIComponent(visit.name)}`)
					.text(`${visit.visit_date} · ${visit.doctor_name || visit.doctor}`)
					.appendTo(card);
				// Notes are displayed as text; attachments are validated paths, assigned through DOM attributes.
				$("<div class='mt-2'>")
					.text(strip_html(visit.remarks || ""))
					.appendTo(card);
				$("<pre class='mt-2'>")
					.text(visit.medication_details || "")
					.appendTo(card);
				(visit.lab_reports || []).forEach((report) => {
					$("<a class='btn btn-default btn-sm mr-2'>")
						.attr("href", `/desk/lab-report/${encodeURIComponent(report.name)}`)
						.text(report.report_type || report.name)
						.appendTo(card);
					if (/^\/private\/files\/[^<>"'\\\r\n]+$/.test(report.report_file || ""))
						$("<a class='btn btn-default btn-sm mr-2'>")
							.attr({
								href: report.report_file,
								target: "_blank",
								rel: "noopener noreferrer",
							})
							.text(__("Download"))
							.appendTo(card);
				});
			});
			offset += (rows || []).length;
			more.text((rows || []).length < 10 ? __("All visits loaded") : __("Load more"));
			more.prop("disabled", (rows || []).length < 10);
		} catch (error) {
			more.prop("disabled", false);
		}
	});
	more.trigger("click");
}
