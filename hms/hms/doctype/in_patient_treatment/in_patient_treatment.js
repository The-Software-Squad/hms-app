// Copyright (c) 2025, nani-samireddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("In Patient Treatment", {
	onload(frm) {
		if (frm.is_new()) return;

		let start = 0;
		const page_length = 10;
		let loading = false;
		let no_more_data = false;

		const container = frm.fields_dict.previous_treatments_html?.wrapper || $("<div>").appendTo(frm.wrapper);
		container.empty();

		function load_previous_treatments() {
			if (loading || no_more_data) return;
			loading = true;

			frappe.call(
				{
					method: "hms.api.patient.get_previous_treatments",
					args: {
						ip_record: frm.doc.in_patient,
						start: start,
						page_size: page_length,
					},
					callback(r) {
						if (r.message || r.message.length === 0) {
							no_more_data = true;
							return;
						}

						r.message.forEach((treatment) => {
							let vitals_html = '';
							if (treatment.vitals && treatment.vitals.length > 0) {
								vitals_html += `<p><strong>Vitals:</strong></p>`;
								// Loop through each vital and display it in table.
							} else {
								vitals_html = "<p>No vitals recorded.</p>";
							}

							// Append treatment details to the container
							const html = `
							<div class="treatment-entry mb-3 p-3 border rounded bg-light">
								<b>Date:</b> ${row.date} <br>
								<b>Doctor:</b> ${row.doctor || "-"} <br>
								<b>Diagnosis:</b> ${row.diagnosis_update || "-"} <br>
								<b>Medications:</b> ${row.medications_given || "-"} <br>
								<b>Vitals:</b> ${vitals_html}
							</div>`;

							container.append(html);
						});

						start += page_length;
						loading = false;
					}
				}
			);
		}

		// Load initial treatments
		load_previous_treatments();

		// Infinite Scroll
		container.on('scroll', function () {
			const scrollTop = container.scrollTop();
			const scrollHeight = container.prop('scrollHeight');
			const containerHeight = container.outerHeight();

			if ((scrollTop + containerHeight) / scrollHeight > 0.7 && !loading) {
				load_visits(page_size, offset);
			}
		});
	},
});
