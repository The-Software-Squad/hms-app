# HMS modules and navigation

HMS is one Frappe application with six functional modules. Its app dock lists them in workflow order. Each ships a curated Sidebar with icons and expandable sections; the User guide link is at the bottom of every sidebar. Standard DocType and action permissions still determine access.

| Dock label | Frappe module / package | Responsibilities |
|---|---|---|
| HMS Core | HMS / `hms.hms` | Patients, patient merge history, hospital settings, simulation rooms, staff, practitioners, departments, overview, analytics, user guide and Hospital Live |
| Reception | HMS Reception / `hms.hms_reception` | Appointments, practitioner schedules and fee eligibility |
| Clinical | HMS Clinical / `hms.hms_clinical` | Consultations, prescription rows, lab requests/results, follow-ups, medication reminders and early departures |
| Inpatient | HMS Inpatient / `hms.hms_inpatient` | Admissions, beds, wards, treatment/vitals and discharge summaries |
| Pharmacy | HMS Pharmacy / `hms.hms_pharmacy` | Medicines/timings, suppliers, intake, stock lots/movements/adjustments, dispensing, returns and handovers |
| Billing | HMS Billing / `hms.hms_billing` | Invoices/credits, payments/refunds, allocation rows, payment purposes and reconciliation |

The original module name **HMS** is retained for shared core ownership. It keeps `/desk/hms/hms-guide`, `/desk/hms/hospital-live` and the original shell available. Patients is also linked from Reception and Clinical; the owning module remains HMS. Cross-module links do not grant additional permissions.

## Source layout

`hms/module_map.py` is the explicit ownership map for all 48 DocTypes and their workspaces, pages, charts, cards and report. Each module's exported metadata, controllers and form/list scripts live together under its package. Shared services (`billing.py`, `stock.py`, `collections.py`, `departures.py`, `workflows.py` and `api/`) retain their existing public paths.

`hms/dock/hms/hms.json` defines the application dock. Each module exports its sidebar at `<module>/sidebar/<module>/<module>.json`. The legacy controller packages under `hms.hms.doctype` re-export public names from their new packages, preserving stored scheduler methods, queued calls and external Python imports.

## Upgrade behavior

The pre-model patch `split_hms_modules` registers ownership on existing metadata before schema sync, and refreshes Frappe's module map so the same migration imports all six modules. Record names, Link targets, DocType names, permission rules and patient/clinical/financial records are retained. This is an ownership change, not a record rename or a ledger conversion.

An existing User or Module Profile that blocks HMS receives matching blocks for the five new modules. The migration is idempotent. Hiding modules remains a navigation preference, separate from document access.

Existing site/user Custom Sidebar arrangements on HMS remain attached to the core module; they are not deleted or silently redistributed. Existing saved HMS dock arrangements that contain the original HMS entry gain the five new module entries, keeping the existing order, pins and hidden state. A saved layout that explicitly omitted HMS is retained; use Manage Dock to add modules to that layout. New installations use the shipped six-module dock.

Old shell-qualified bookmarks can still resolve their record or workspace through the HMS shell; Desk selects the owning sidebar as appropriate. Direct record names and source DocType references used by WhatsApp rules and Print Formats stay the same.

## Verification

Run regressions only on the dedicated workflow test site:

```sh
bench --site hms-workflow-test.localhost migrate
bench --site hms-workflow-test.localhost execute hms.tests.test_workflows.run
bench --site hms-workflow-test.localhost execute hms.tests.test_modules.run
bench --site hms-workflow-test.localhost execute hms.tests.test_hospital_live.run
python3 scripts/validate_user_guides.py
```

A release also needs clean-install and upgrade checks, preservation of existing records/permissions, and browser checks for the dock, module switching, old bookmarks, guide and Hospital Live. WhatsApp integration checks run separately on its dedicated disposable site with external transport blocked.
