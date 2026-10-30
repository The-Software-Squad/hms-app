frappe.ui.form.on("Patient", {
	refresh(frm) {
		const clinical = frappe.user_roles.some((role) =>
			["Doctor", "System Manager"].includes(role)
		);
		if (!frm.is_new()) {
			if (frappe.model.can_create("Patient Visit"))
				frm.add_custom_button(
					__("New Walk-in Visit"),
					() => frappe.new_doc("Patient Visit", { patient: frm.doc.name }),
					__("Create")
				);
			if (frappe.model.can_create("Patient Appointment"))
				frm.add_custom_button(
					__("Book Appointment"),
					() => frappe.new_doc("Patient Appointment", { patient: frm.doc.name }),
					__("Create")
				);
			if (frappe.model.can_create("IP Record"))
				frm.add_custom_button(
					__("New Admission"),
					() => frappe.new_doc("IP Record", { patient: frm.doc.name }),
					__("Create")
				);
			for (const [label, doctype] of [
				["Visits", "Patient Visit"],
				["Lab Reports", "Lab Report"],
				["Admissions", "IP Record"],
				["Treatments", "In Patient Treatment"],
			]) {
				if (frappe.model.can_read(doctype))
					frm.add_custom_button(
						__(label),
						() => frappe.set_route("List", doctype, { patient: frm.doc.name }),
						__("View")
					);
			}
			if (clinical) render_patient_history(frm);
			if (frappe.user_roles.includes("System Manager"))
				frm.add_custom_button(
					__("Merge Duplicate"),
					() => {
						frappe.prompt(
							[
								{
									fieldname: "target",
									fieldtype: "Link",
									options: "Patient",
									label: __("Keep this patient"),
									reqd: 1,
								},
								{
									fieldname: "reason",
									fieldtype: "Small Text",
									label: __("Reason"),
									reqd: 1,
								},
							],
							(values) => {
								frappe.confirm(
									__(
										"Merge this patient into {0}? Review identifiers and history first. This action is permanent.",
										[frappe.utils.escape_html(values.target)]
									),
									() =>
										frappe.call({
											method: "hms.api.registration.merge_patients",
											type: "POST",
											args: { source: frm.doc.name, ...values },
											callback: (r) =>
												frappe.set_route(
													"Form",
													"Patient",
													r.message.patient
												),
										})
								);
							},
							__("Review Patient Merge")
						);
					},
					__("Actions")
				);
		}
		const duplicates = frm.doc.__onload?.duplicate_candidates || [];
		const wrapper = frm.fields_dict.duplicate_candidates?.$wrapper;
		if (wrapper) {
			wrapper.empty();
			if (duplicates.length) {
				$("<p>")
					.text(
						__(
							"Possible duplicates: review these records; shared names or family phone numbers do not prove a duplicate."
						)
					)
					.appendTo(wrapper);
				duplicates.forEach((patient) =>
					$("<a>")
						.attr("href", `/desk/patient/${encodeURIComponent(patient.name)}`)
						.text(`${patient.patient_name} (${patient.name})`)
						.addClass("btn btn-default btn-sm mr-2")
						.appendTo(wrapper)
				);
			}
		}
		update_patient_age(frm);
	},
	dob: update_patient_age,
});

function update_patient_age(frm) {
	const wrapper = frm.fields_dict.age_html?.$wrapper;
	if (!wrapper) return;
	wrapper.empty();
	if (!frm.doc.dob) return;
	const birth = frappe.datetime.str_to_obj(frm.doc.dob),
		today = new Date();
	let years = today.getFullYear() - birth.getFullYear();
	if (
		today.getMonth() < birth.getMonth() ||
		(today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())
	)
		years--;
	$("<span>")
		.text(years >= 1 ? `${years} years` : __("Under one year"))
		.appendTo(wrapper);
}

function render_patient_history(frm) {
	const wrapper = frm.fields_dict.previous_visits?.$wrapper;
	if (!wrapper) return;
	wrapper.empty();
	const list = $("<div>").appendTo(wrapper);
	let offset = 0;
	const more = $("<button type='button' class='btn btn-default btn-sm'>")
		.text(__("Load visits"))
		.appendTo(wrapper);
	more.on("click", async () => {
		more.prop("disabled", true);
		try {
			const { message: visits } = await frappe.call({
				method: "hms.api.patient.get_previous_patient_visits",
				args: { patient: frm.doc.name, limit: 10, offset },
			});
			(visits || []).forEach((visit) =>
				$("<a>")
					.attr("href", `/desk/patient-visit/${encodeURIComponent(visit.name)}`)
					.text(
						`${visit.visit_date} · ${visit.doctor_name || visit.doctor} · ${
							visit.name
						}`
					)
					.addClass("d-block mb-2")
					.appendTo(list)
			);
			offset += (visits || []).length;
			more.text((visits || []).length < 10 ? __("All visits loaded") : __("Load more"));
			more.prop("disabled", (visits || []).length < 10);
		} catch (error) {
			more.prop("disabled", false);
		}
	});
	more.trigger("click");
}
