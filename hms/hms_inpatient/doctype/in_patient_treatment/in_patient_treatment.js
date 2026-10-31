frappe.ui.form.on("In Patient Treatment", {
	refresh(frm) {
		if (frm.is_new()) return;
		const wrapper = frm.fields_dict.previous_treatments?.$wrapper;
		if (!wrapper) return;
		wrapper.empty();
		const list = $("<div>").appendTo(wrapper);
		const more = $("<button type='button' class='btn btn-default btn-sm'>")
			.text(__("Load treatment history"))
			.appendTo(wrapper);
		let start = 0;
		more.on("click", async () => {
			more.prop("disabled", true);
			try {
				const { message: rows } = await frappe.call({
					method: "hms.api.patient.get_previous_treatments",
					args: {
						ip_record: frm.doc.in_patient,
						exclude_treatment: frm.doc.name,
						start,
						page_length: 10,
					},
				});
				(rows || []).forEach((row) => {
					const card = $("<div class='border rounded p-3 mb-3'>").appendTo(list);
					$("<a>")
						.attr("href", `/desk/in-patient-treatment/${encodeURIComponent(row.name)}`)
						.text(`${row.date} · ${row.doctor || ""}`)
						.appendTo(card);
					for (const value of [row.diagnosis_update, row.medications_given])
						$("<div>")
							.text(strip_html(value || ""))
							.appendTo(card);
					(row.vitals || []).forEach((v) =>
						$("<p>")
							.text(
								`${v.time}: ${v.temperature ?? "—"} °F; pulse ${
									v.pulse ?? "—"
								}; BP ${v.blood_pressure || "—"}; respirations ${
									v.respiratory_rate ?? "—"
								}; ${v.recorded_by || ""}`
							)
							.appendTo(card)
					);
				});
				start += (rows || []).length;
				more.text((rows || []).length < 10 ? __("All history loaded") : __("Load more"));
				more.prop("disabled", (rows || []).length < 10);
			} catch (error) {
				more.prop("disabled", false);
			}
		});
		more.trigger("click");
	},
});
