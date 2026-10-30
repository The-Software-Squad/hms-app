import frappe


def execute():
	"""Use standard Patient list for existing HMS application icons."""
	if not frappe.db.exists("DocType", "Desktop Icon"):
		return
	for name in frappe.get_all("Desktop Icon", filters={"app": "hms", "icon_type": "App"}, pluck="name"):
		if frappe.db.get_value("Desktop Icon", name, "link") in ("/hms", "/app/hms", "/desk/hms"):
			frappe.db.set_value("Desktop Icon", name, "link", "/desk/patient")
