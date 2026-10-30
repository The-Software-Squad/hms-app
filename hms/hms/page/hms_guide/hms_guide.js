/* global hms */
frappe.pages["hms-guide"].on_page_load = function (wrapper) {
	frappe.require("/assets/hms/js/user_guide.js", () => {
		wrapper.hms_user_guide = new hms.UserGuide(wrapper);
	});
};
frappe.pages["hms-guide"].on_page_show = function (wrapper) {
	wrapper.hms_user_guide?.show();
};
