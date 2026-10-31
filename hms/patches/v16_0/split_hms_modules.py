"""Move metadata ownership without renaming patient, clinical or financial records."""

import frappe

from hms.module_map import ENTITY_MODULES, MODULES


def execute():
	# Migration may have initialized the module map from an earlier release's
	# cache. Model sync in this same process must walk every new module folder.
	frappe.clear_cache()
	frappe.setup_module_map()
	# Migrate before model sync so controllers and code-backed workspaces resolve in
	# their new packages even when a site's workspace was edited after its export.
	for doctype, entries in ENTITY_MODULES.items():
		for name, module in entries.items():
			if module != "HMS" and frappe.db.get_value(doctype, name, "module") == "HMS":
				frappe.db.set_value(doctype, name, "module", module, update_modified=False)
	preserve_module_visibility()
	frappe.clear_cache()


def preserve_module_visibility():
	# An existing preference to hide all of HMS must continue to hide its new
	# modules. This changes navigation only; document permissions remain untouched.
	for row in frappe.get_all(
		"Block Module", filters={"module": "HMS"}, fields=["parent", "parenttype", "parentfield"]
	):
		if row.parenttype not in ("User", "Module Profile") or row.parentfield != "block_modules":
			continue
		filters = {key: row[key] for key in ("parent", "parenttype", "parentfield")}
		existing = set(frappe.get_all("Block Module", filters=filters, pluck="module"))
		index = frappe.db.count("Block Module", filters)
		for module in MODULES:
			if module in existing:
				continue
			index += 1
			frappe.get_doc({"doctype": "Block Module", **filters, "idx": index, "module": module}).db_insert()
		if row.parenttype == "User":
			frappe.clear_cache(user=row.parent)
