import frappe


def execute():
	"""Point existing HMS app icons to its website frontend."""
	if not frappe.db.exists("DocType", "Desktop Icon"):
		return
	for name in frappe.get_all("Desktop Icon", filters={"app": "hms", "icon_type": "App"}, pluck="name"):
		if frappe.db.get_value("Desktop Icon", name, "link") in ("/app/hms", "/desk/hms"):
			frappe.db.set_value("Desktop Icon", name, "link", "/hms")
