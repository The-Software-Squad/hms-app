# HMS user guide plan

Updated 22 October 2026. This guide follows the task-based structure of the local WhatsApp Messaging guide. It covers standard Frappe Desk; the removed React frontend is out of scope.

## Delivery

Use one structured workflow manifest as the source for a searchable in-app **User guide** and generated repository Markdown. Provide bookmarkable `/desk/hms-guide/<workflow>` links, role/category labels, related guides and Help → User guide links on relevant forms. Add a guide entry to Reception, Doctor, Pharmacist, Accounts and Follow-ups workspaces. Screenshots should enlarge without hiding the steps, with extra screenshots expandable on long forms. Plan downloadable print/PDF export after the verified content and screenshots are ready.

## Page structure

Each page must include: plain-language purpose, who can perform it, prerequisites, numbered steps with exact labels, what success looks like, common errors and recovery, role limitations, related workflows, screenshots captured from coherent example records with realistic names and medicines and the date/version last verified. Distinguish queued email from sent mail; stock drafts from posted movements; payment drafts from posted receipts; discharge drafts from finalized discharge. Do not describe planned controls as released behavior.

## Chapters and acceptance evidence

| Guide | Roles | Verification and screenshot |
|---|---|---|
| Find your way around and your permissions | All staff | Desk chooser/workspaces, role-specific navigation, empty/error states |
| Find, register and update a patient | Reception, Doctor | Search existing patients, duplicate warning, demographic/contact update |
| Review and merge duplicate patients | System Manager | Source/target preview, conflict warnings, reason, preserved audit |
| Configure staff, doctors and schedules | System Manager; Reception for schedules | Employee/User mapping, active practitioner, weekday slots and rejected overlaps |
| Book or reschedule an appointment | Reception | Valid available slot, conflict error, cancel/rebook boundary |
| Check in a booked or walk-in patient | Reception | Check In action, department, one linked visit, retry behavior |
| Record a consultation and corrections | Doctor | Clinical history, findings, status, finalization and correction reason |
| Request, receive and review a lab report | Reception, Doctor | Matching patient/visit, private uploaded file, reviewed state |
| Prescribe and send medication reminders | Doctor | Schedule preview, elapsed-day duration, send permission, queued/sent/failed tracking |
| Manage clinical follow-ups | Reception, Doctor | Due/overdue list, contact note, schedule and close action |
| Understand free follow-up eligibility | Reception, Doctor, System Manager | Initial visit versus allowed free visits, expiry, cancellation, paid episode |
| Admit, allocate a bed and transfer | Reception | Active admission, bed occupancy and transfer conflict |
| Record inpatient care and vitals | Doctor | Patient/admission match, units, author and chronological validation |
| Finalize discharge or reopen admission | Doctor | Summary, atomic bed release, finalized state, explicit reopening reason |
| Receive medicines and inspect stock lots | Pharmacist | Draft → Post, source/batch/expiry/rate and resulting available quantity |
| Dispense, return or adjust medicines | Pharmacist | Prescription linkage, insufficient/expired stock error, return cap, adjustment reason and ledger |
| Issue invoices and record/refund payments | Reception, Pharmacist, System Manager | Invoice/credit, allocation, posting, immutability, refund limits and reconciliation |
| Read dashboards and investigate discrepancies | System Manager; relevant operational roles | Due lists, census, collection definitions, invoice/stock reconciliation, delivery failure |

## Example data and release gates

Use only `hms-workflow-test.localhost` with coherent hospital/staff/patient examples, actual medicine names and reserved example contact destinations. No real patients, operational stock, credentials, private files or real mail/provider connections may appear in public guide assets. Seed only the disposable site; leave its scheduler disabled and mock email/provider calls. Capture the actual tested application through the browser, never fabricated UI images.

Sequence: complete and test a workflow → write its instructions → prepare a coherent example → capture each referenced action/result → verify role, search, deep links and narrow viewport → regenerate Markdown → mark that page verified. Keep a pending screenshot checklist until every image is captured and reviewed. Any later button/status/permission change must update the manifest, screenshots and tests together.

The source of truth is `hms/public/docs/user-guide.json`, page rendering in a standard `hms-guide` Page, and generated files under `docs/user-guide/`. This document plans those deliverables; it does not claim the guide UI or screenshots have already shipped.

## Upgrade and historical records

Include an administrator chapter explaining **Legacy** stock documents and **Legacy Recorded** receipts. Upgrades retain earlier records; they do not infer a stock ledger or invent invoice allocations. Verify physical opening stock before posting a new opening intake. Historical receipts retain their amount/date/payer and can be explicitly allocated and posted for reconciliation. Explain that dashboard receipts are gross recorded receipts before refunds; use Reconciliation for net allocated receipts, credits, outstanding amounts and refund dues. Do not imply the ledger covers unreviewed legacy stock or unallocated historical cash.

## Implementation sequence

1. Build the HMS-owned manifest, guide Page, search, chapter deep links and help-menu helper. Reuse the WhatsApp guide's interaction pattern while keeping HMS independent of that app.
2. Deliver registration, booking/check-in, consultation/labs/reminders, admissions/discharge and pharmacy/payment chapters first; verify each under its actual staff role.
3. Complete setup, duplicate review, eligibility, follow-up outreach, reporting and upgrade chapters. Capture narrow and wide viewport examples, empty states and common errors.
4. Review every screenshot against the final buttons, regenerate repository Markdown, verify links and search, and record the application revision/date for each chapter. Add printable export after this review.

## Documentation delivery status — 22 October 2026

Written instructions cover 21 workflows. The current guide reflects the corrected appointment progression, cancellation dependencies, full-credit/refund retention, historical follow-up eligibility by actual visit date and mandatory bed allocation. Admissions and important settings now retain change history. The departure chapter covers early exits and pending lab ownership; pharmacy instructions cover real handovers, return origins, quarantine release and disposal.

The guide currently references zero screenshots and zero GIFs. Older selected-frame media is superseded. Continuous cursor-visible recordings and matching stills remain pending; no chapter is marked fully verified. The offline bundle is regenerated from the current manifest so it cannot claim the old media is current.

See [the staff guide](user-guide/README.md), [current media checklist](USER-GUIDE-MEDIA-STATUS.md), [quick reference](USER-GUIDE-QUICK-REFERENCE.md) and [maintenance instructions](USER-GUIDE-MAINTENANCE.md).
