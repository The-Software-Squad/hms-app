"""Carry an existing HMS dock arrangement into the six-module navigation."""

import frappe

from hms.module_map import MODULES


def execute():
	for name in frappe.get_all("Dock", filters={"app": "hms", "standard": 0}, pluck="name"):
		doc = frappe.get_doc("Dock", name)
		core = next((row for row in doc.items if row.link_type == "Sidebar" and row.link_to == "HMS"), None)
		if not core:
			# A layout that explicitly omitted HMS retains that choice.
			continue
		existing = {(row.link_type, row.link_to) for row in doc.items}
		changed = False
		for module in MODULES[1:]:
			if ("Sidebar", module) in existing:
				continue
			doc.append(
				"items", {"link_type": "Sidebar", "link_to": module, "hidden": core.hidden, "added": 0}
			)
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
