# Hospital Live

Hospital Live is the action-driven, read-only 3D operations page in HMS Desk. Open `/desk/hms/hospital-live` or the **Hospital Live · 3D** sidebar link. It runs on standalone Frappe/HMS without restoring the removed React dashboard.

The [staff guide](user-guide/hospital-live.md) covers room setup, navigation, names, availability and exceptions.

## Record-to-character contract

| Saved HMS action/state | Scene projection |
|---|---|
| Scheduled appointment | Booked count only; no patient character before check-in |
| Patient Visit Checked In | Seated in the assigned doctor's waiting section; overflow stands beyond configured seats |
| Under Consultation | Inside the treating doctor's room; active patient listed in room inspector |
| Lab/Diagnostics Pending | Diagnostics area |
| Lab/Diagnostics Completed | Returns to the doctor's waiting area for review |
| Prescription Given | Next-step area; pharmacy if a tracked posted sale is still uncollected |
| Completed / Closed Early / Cancelled / No Show | Visit leaves active floor; its record remains in HMS |
| Posted sale Not Collected / Partly Collected | Pharmacy collection activity; full handover or full return removes that sale from the pending queue |
| Active IP Record | Patient at allocated bed; takes precedence over an outpatient avatar for the same patient |
| Finalized discharge / inpatient departure | Admission leaves the active scene and bed occupancy is refreshed |
| Doctor reports Available | Doctor character in the configured room for the reported day |
| Away / Off Duty / no report today | No idle doctor character; an active consultation is still represented as recorded activity |

A patient gets one avatar. Active admissions take precedence, followed by active consultation, diagnostics and queue records. Multiple active visit records remain available for review in the activity list. Doctor room queues are ordered by saved visit creation time and then readable visit number; this is an operational ordering, not a physical queue-position sensor. No consultation duration, wait estimate or future movement is invented.

Earlier unclosed outpatient visits appear as review exceptions, rather than occupying today's waiting seats. Admissions remain active across dates until closed. Pharmacy counts represent tracked uncollected sale records, not a proven number of people physically at the counter.

## Configuration and access

Hospital Settings contains the HMS Simulation Room child table: active practitioner, unique room name, 1–24 waiting seats and enabled flag. Enabled row order controls room order. With no configuration, active visible doctors receive eight-seat rooms. Disabled configured doctors retain their permitted activity records in the list but have no assigned room in the scene.

The page/API requires an HMS staff role. Every record list uses `frappe.get_list`, preserving record permissions and user restrictions. The endpoint returns operational labels/states only; no contact data, diagnosis, prescription contents, HR details or monetary values are requested. Patient names start hidden, with an explicit reveal toggle. Room settings are projected through a narrow operational view; the rest of Hospital Settings remains administrator-only.

Availability is a separate authorized POST action. A linked Doctor can report their own status; a System Manager can report any active doctor. Server-owned status/time/actor fields cannot be forged by editing the practitioner master. Availability changes retain normal Frappe version history and expire to Not Recorded on a new site date. Neither schedule membership nor account login proves presence.

## Rendering and synchronization

- Three.js 0.180.0 is vendored locally with its MIT license; no runtime CDN, third-party telemetry, patient-data export, Node service or new frontend build is required.
- The model is a deterministic projection of the current authorized snapshot. First load places actors directly; subsequent saved stage changes animate schematic paths. It does not replay every event between snapshots.
- Polls run every 15 seconds only while the page is visible. In-flight refreshes cannot overlap; page hide stops polling and animation, and reduced-motion disables walking transitions.
- Rendering is on demand while idle; display pixel ratio is capped at 1.5. Shared geometry/materials and limits of 160 patient avatars/24 beds keep laptop resource use bounded. Six doctor rooms display per view, with explicit navigation and counts.
- Each source list is capped at 1,000 rows and returns a truncation notice. Counts then describe the retrieved permitted subset. The accessible activity list shows 200 rows per filter; original HMS lists remain authoritative for full records.
- Connection failures retain a marked stale snapshot. Permission failures clear operational content. WebGL failure leaves the activity list usable.
- Orbit, pan, zoom, top view, reset, expand, room/person selection and source-form navigation are supported. Camera movement never writes clinical records.

## Verification commands

On the disposable workflow-test site only:

```sh
bench --site hms-workflow-test.localhost execute hms.tests.test_hospital_live.run
bench --site hms-workflow-test.localhost execute hms.tests.test_workflows.run
node --test hms/tests/test_hospital_live_model.mjs
python3 scripts/export_user_guides.py
python3 scripts/validate_user_guides.py
```

Example records for visual review are created only through HMS controllers on the isolated test site, with reserved contact destinations and mocked background messaging. The simulation page has no demo mode that silently replaces live records.

Visual direction references: [openWCS hardware visualisation](https://openwcs.ai/hardware-visualisation) and [Three.js documentation](https://threejs.org/docs/). The hospital layout, figures, furniture, model and HMS integration are implemented here.
