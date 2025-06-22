// Copyright (c) 2025, nani-samireddy and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Patient Visit", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Patient Visit', {
	refresh(frm) {
		if (!frm.doc.__islocal && frm.doc.patient) {
			const wrapper = frm.fields_dict.previous_visits.$wrapper;
			wrapper.html('<div id="visit-container" style=" padding: 8px;"></div>');

			let offset = 0;
			const page_size = 10;
			const initial_load = 7;
			let loading = false;
			const container = wrapper.find('#visit-container');

			function render_visits(visits) {
				visits.forEach(v => {
					const visitDate = frappe.datetime.str_to_user(v.visit_date || '');
					const followUp = v.follow_up ? frappe.datetime.str_to_user(v.follow_up) : '—';
					const doctor = v.doctor || '—';
					// Handle lab reports
					let reports_html = '';
					if (v.lab_reports && v.lab_reports.length > 0) {
						reports_html += `<p><strong>Lab Reports:</strong><ul style="padding-left: 16px;">`;
						v.lab_reports.forEach(report => {
							const reportDate = report.received_on ? frappe.datetime.str_to_user(report.received_on) : '—';
							const link = report.report_file
								? `<a href="${report.report_file}" target="_blank" style="margin-left: 6px;" class="btn btn-sm btn-secondary">Download</a>`
								: '';
							const docLink = `<a href="/app/lab-report/${report.name}" target="_blank" style="margin-left: 6px;" class="btn btn-sm btn-secondary">Open Doc</a>`;
							reports_html += `<li>${frappe.utils.escape_html(report.report_type || 'Unnamed')} (${reportDate}) ${link} ${docLink}</li>`;
						});
						reports_html += `</ul></p>`;
					}

					container.append(`
	  <div class="visit-entry" style="margin-bottom: 16px; padding: 12px; border: 1px solid #d1d8dd; border-radius: 6px;">
		<div class="visit-header" style="
		display: grid;
		grid-template-columns: 2fr 2fr 1fr;
		column-gap: 12px;
		row-gap: 4px;
		align-items: center;
		margin-bottom: 18px;
		">
			<div>
				<strong>Visit Date:&nbsp;</strong> ${visitDate}<br>
				<strong>Follow-Up:</strong> ${followUp}
			</div>
			<div>
				<strong>Doctor:</strong> ${frappe.utils.escape_html(doctor)}
			</div>
			<div style="text-align: right;">
				<a href="/app/patient-visit/${v.name}" target="_blank" class="btn btn-sm btn-primary">
				Edit Details
				</a>
			</div>
		</div>
		<div class="report-details" style="margin-bottom: 12px;">
		${reports_html}
		</div>
		<p><strong>Remarks:</strong><br>
		  <pre style="white-space: pre-wrap; margin: 4px 0;">${v.remarks || '—'}</pre>
		</p>
		<p><strong>💊 Medications:</strong><br>
		  <pre style="white-space: pre-wrap; margin: 4px 0;">${frappe.utils.escape_html(v.medication_details || '—')}</pre>
		</p>
	  </div>
	`);
				});
			}

			function load_visits(limit, start = 0) {
				if (loading) return;
				loading = true;
				frappe.call({
					method: 'hms.api.patient.get_previous_patient_visits',
					args: {
						patient: frm.doc.patient,
						exclude_visit: frm.doc.name,
						limit,
						offset: start
					},
					callback(r) {
						if (r.message && r.message.length > 0) {
							render_visits(r.message);
							offset += r.message.length;
						}
						loading = false;
					}
				});
			}

			// Load initial 7
			load_visits(initial_load);

			// Infinite Scroll
			container.on('scroll', function () {
				const scrollTop = container.scrollTop();
				const scrollHeight = container.prop('scrollHeight');
				const containerHeight = container.outerHeight();

				if ((scrollTop + containerHeight) / scrollHeight > 0.7 && !loading) {
					load_visits(page_size, offset);
				}
			});
		}
	}
});
