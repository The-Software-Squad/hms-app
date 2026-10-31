"""Module ownership, navigation and upgrade compatibility on the isolated site."""

from importlib import import_module
from unittest import TestSuite, TextTestRunner

import frappe
from frappe.model.base_document import get_controller

from hms.module_map import ENTITY_MODULES, MODULES
from hms.tests.test_workflows import TestHMSWorkflows


class TestHMSModules(TestHMSWorkflows):
	def test_entities_resolve_to_their_owning_modules(self):
		for doctype, entries in ENTITY_MODULES.items():
			for name, module in entries.items():
				self.assertEqual(frappe.db.get_value(doctype, name, "module"), module, (doctype, name))
		for name, module in ENTITY_MODULES["DocType"].items():
			controller = get_controller(name)
			self.assertTrue(controller.__module__.startswith("hms." + frappe.scrub(module) + "."), name)

	def test_dock_offers_six_modules_with_distinct_menus(self):
		from frappe.desk.doctype.dock.dock import get_app_dock
		from frappe.desk.doctype.sidebar.sidebar import resolve_sidebar

		rows = get_app_dock("hms")
		self.assertEqual([row["link_to"] for row in rows], list(MODULES))
		self.assertTrue(all(row["icon"] for row in rows))
		menus = {}
		for module in MODULES:
			sidebar = resolve_sidebar(module, "Administrator")
			self.assertIsNotNone(sidebar, module)
			self.assertFalse(sidebar.computed)
			menus[module] = {row.get("link_to") for row in sidebar.items}
		self.assertIn("Patient Appointment", menus["HMS Reception"])
		self.assertNotIn("Meds Out", menus["HMS Reception"])
		self.assertIn("Meds Out", menus["HMS Pharmacy"])
		self.assertNotIn("Lab Report", menus["HMS Pharmacy"])
		self.assertIn("HMS Invoice", menus["HMS Billing"])

	def test_legacy_public_controller_imports_remain_compatible(self):
		for name, module in ENTITY_MODULES["DocType"].items():
			if module == "HMS":
				continue
			slug = frappe.scrub(name)
			old = import_module(f"hms.hms.doctype.{slug}.{slug}")
			new = import_module(f"hms.{frappe.scrub(module)}.doctype.{slug}.{slug}")
			# Frappe's actual controller name is authoritative for acronyms/case.
			controller_name = get_controller(name).__name__
			self.assertIs(getattr(old, controller_name), getattr(new, controller_name))
		old = import_module("hms.hms.doctype.fee_validity.fee_validity")
		new = import_module("hms.hms_reception.doctype.fee_validity.fee_validity")
		self.assertIs(old.update_validity_status, new.update_validity_status)

	def test_upgrade_refreshes_cached_modules_and_preserves_block_preferences(self):
		from frappe.boot import get_module_sidebars

		from hms.patches.v16_0.split_hms_modules import execute

		self.reception.append("block_modules", {"module": "HMS"})
		self.reception.save()
		stale = dict(frappe.local.app_modules)
		stale["hms"] = ["hms"]
		frappe.cache.set_value("app_modules", stale)
		frappe.local.app_modules = stale
		execute()
		execute()
		self.assertEqual(frappe.local.app_modules["hms"], [frappe.scrub(module) for module in MODULES])
		self.reception.reload()
		self.assertEqual(sorted(row.module for row in self.reception.block_modules), sorted(MODULES))
		frappe.set_user(self.reception.name)
		self.assertTrue(set(MODULES).isdisjoint(get_module_sidebars()))
		# A hidden module remains a navigation preference, not a document permission.
		self.assertTrue(frappe.has_permission("Patient Appointment", "read"))

	def test_existing_dock_order_pins_and_hidden_preferences_survive(self):
		from hms.patches.v16_0.migrate_hms_dock import execute

		dock = frappe.get_doc(
			{
				"doctype": "Dock",
				"app": "hms",
				"user": self.reception.name,
				"items": [
					{
						"link_type": "Workspace",
						"link_to": "Reception Dashboard",
						"added": 1,
						"icon": "calendar",
						"title": "My reception",
					},
					{"link_type": "Sidebar", "link_to": "HMS", "hidden": 1},
				],
			}
		).insert()
		execute()
		execute()
		dock.reload()
		self.assertEqual(dock.items[0].link_to, "Reception Dashboard")
		self.assertEqual(dock.items[0].title, "My reception")
		modules = [row for row in dock.items if row.link_type == "Sidebar"]
		self.assertEqual([row.link_to for row in modules], list(MODULES))
		self.assertTrue(all(row.hidden for row in modules))


def run():
	if frappe.local.site != "hms-workflow-test.localhost":
		raise RuntimeError("Refusing operational site")
	names = [name for name in TestHMSModules.__dict__ if name.startswith("test_")]
	result = TextTestRunner(verbosity=2).run(TestSuite(TestHMSModules(name) for name in names))
	if not result.wasSuccessful():
		raise RuntimeError("HMS module regressions failed")
	return dict(tests=result.testsRun, failures=0, errors=0)
