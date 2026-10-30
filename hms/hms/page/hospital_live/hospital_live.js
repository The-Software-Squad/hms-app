/* global hms */
frappe.pages["hospital-live"].on_page_load = function (wrapper) {
	const version = "20261029-2";
	const stylesheet = document.createElement("link");
	stylesheet.rel = "stylesheet";
	stylesheet.href = `/assets/hms/css/hospital_live.css?v=${version}`;
	document.head.appendChild(stylesheet);
	import(`/assets/hms/js/hospital_live.js?v=${version}`)
		.then(() => {
			wrapper.hospital_live = new hms.HospitalLive(wrapper);
			if ($(wrapper).is(":visible")) wrapper.hospital_live.show();
		})
		.catch(() => {
			$(wrapper)
				.empty()
				.append(
					$('<p class="text-muted p-4">').text(
						__("Hospital Live could not load. Refresh this page to try again.")
					)
				);
		});
};
frappe.pages["hospital-live"].on_page_show = function (wrapper) {
	wrapper.hospital_live?.show();
};
