// Copyright (c) 2025, nani-samireddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("In Patient Treatment", {
	onload(frm) {
		if (frm.is_new()) return;

		let offset = 0;
		const page_size = 10;
		let loading = false;
		let no_more_data = false;

		const wrapper = frm.fields_dict.previous_treatments?.$wrapper;
		wrapper.html('<div id="treatment-container" style="padding: 8px;"></div>');
		const container = wrapper.find("#treatment-container");

		function render_treatments(treatments) {
			treatments.forEach(t => {
				const treatmentDate = frappe.datetime.str_to_user(t.date || '');
				const doctor = t.doctor || '—';
				const diagnosis = t.diagnosis_update || '—';
				const meds = t.medications_given || '—';

				// Build vitals table
				let vitals_html = '';
				if (t.vitals && t.vitals.length > 0) {
					vitals_html += `
					<p><strong>Vitals:</strong></p>
					<div class="table-responsive">
					<table class="table table-bordered table-sm">
						<thead class="table-light">
							<tr>
								<th>Time</th>
								<th>Temp (°F)</th>
								<th>Pulse</th>
								<th>BP</th>
								<th>Resp. Rate</th>
								<th>Recorded By</th>
							</tr>
						</thead>
						<tbody>
					`;

					t.vitals.forEach(v => {
						vitals_html += `
							<tr>
								<td>${v.time || '-'}</td>
								<td>${v.temperature ?? '-'}</td>
								<td>${v.pulse ?? '-'}</td>
								<td>${v.blood_pressure || '-'}</td>
								<td>${v.respiratory_rate ?? '-'}</td>
								<td>${frappe.utils.escape_html(v.recorded_by || '-')}</td>
							</tr>`;
					});

					vitals_html += `
						</tbody>
					</table>
					</div>`;
				} else {
					vitals_html = `<p><strong>Vitals:</strong> No vitals recorded.</p>`;
				}

				// Append treatment card
				container.append(`
<div class="treatment-entry" style="margin-bottom: 16px; padding: 12px; border: 1px solid #d1d8dd; border-radius: 6px;">
	<div class="treatment-header" style="
		display: grid;
		grid-template-columns: 2fr 2fr 1fr;
		column-gap: 12px;
		row-gap: 4px;
		align-items: center;
		margin-bottom: 18px;
	">
		<div>
			<strong>Date:</strong> ${treatmentDate}<br>
			<strong>Doctor:</strong> ${frappe.utils.escape_html(doctor)}
		</div>
		<div>
			<a href="/app/in-patient-treatment/${t.name}" target="_blank" class="btn btn-sm btn-primary">
			Edit Details
			</a>
		</div>
	</div>
	${vitals_html}
	<p><strong>Diagnosis:</strong><br>
		<pre style="white-space: pre-wrap; margin: 4px 0;">${diagnosis}</pre>
	</p>
	<p><strong>💊 Medications:</strong><br>
		<pre style="white-space: pre-wrap; margin: 4px 0;">${meds}</pre>
	</p>
</div>
				`);
			});
		}

		function load_treatments() {
			if (loading || no_more_data) return;
			loading = true;

			frappe.call({
				method: "hms.api.patient.get_previous_treatments",
				args: {
					ip_record: frm.doc.in_patient,
					start: offset,
					page_length: page_size,
					exclude_treatment: frm.doc.name
				},
				callback(r) {
					const data = r.message || [];
					if (data.length === 0) {
						no_more_data = true;
					} else {
						render_treatments(data);
						offset += data.length;
					}
					loading = false;
				}
			});
		}

		// Initial load
		load_treatments();

		// Infinite Scroll
		container.on('scroll', function () {
			const scrollTop = container.scrollTop();
			const scrollHeight = container.prop('scrollHeight');
			const containerHeight = container.outerHeight();

			if ((scrollTop + containerHeight) / scrollHeight > 0.7 && !loading) {
				load_treatments();
			}
		});
	}
});
