# Standalone HMS workflows

HMS runs on Frappe Desk without ERPNext. Hospital Settings controls the consultation fee fallback, currency and free follow-up policy. A department fee takes precedence when positive. A zero fee creates no consultation invoice. These are operational invoices and receipts; no payment gateway, general ledger, tax accounting, payroll, patient portal or external laboratory adapter is included.

## Live hospital schematic

Hospital Live projects permitted HMS actions into 3D rooms, waiting seats and care areas, with a readable activity list and explicit reported doctor availability. It is a schematic operational view, not a physical-location sensor. [Configuration and action mapping](HOSPITAL-LIVE.md).

## Roles and identity

System Manager configures staff, settings and permissions, and reviews explicit patient merges. Receptionist registers patients, books/checks in visits, manages beds and admissions, receives private laboratory files, and records payments. Doctor records consultations, prescriptions, results review, inpatient care and finalized discharge. Pharmacist receives, dispenses, returns and adjusts medicines, and records pharmacy payments. Clinical-history APIs require clinical roles as well as document permissions. Salary, personal employee details and clinical notes use separate permission levels. Site-specific user permissions and custom permission rules still apply.

Practitioners link to an active Employee and enabled Doctor-role User. Patient identifiers remain distinct even when names or phone numbers match. Duplicate warnings prompt review; only an administrator can merge, with a reason and audit snapshot. Conflicting identifiers, simultaneous admissions and financial records on the source patient block merging for manual reconciliation.

## Outpatient care

1. Search before registration; update the patient's own demographic and contact fields.
2. Book a scheduled practitioner slot with a department, start and end time. Missing end time is filled server-side with 30 minutes; the entire appointment must fit the shift. Overlaps are rejected.
3. Use Check In once; retries reuse the linked visit. A walk-in can start directly from Patient → Create → New Walk-in Visit.
4. The doctor reviews history, records findings, requests reports and writes a dated prescription. Laboratory reports must reference the same visit and patient, use private uploaded files, and be reviewed or cancelled before consultation completion.
5. Complete the visit with findings. Completed, Closed Early and cancelled visits retain their identity and history. Amendments to completed or Closed Early notes/prescriptions need a new correction reason.
6. Record a clinical follow-up date and outreach status/notes. Book Follow-up links the appointment to the original visit; cancelling restores its pending queue state. The due list excludes missing and future follow-up dates.

Clinical follow-ups are separate from fee eligibility. When enabled, an eligibility window includes the initial visit date: seven days means that date through six days later. The free visit cap excludes the initial paid visit. Eligibility uses the actual visit date: historically valid Expired/Completed windows may still provide a remaining allowance for a backdated visit. Cancelled windows never qualify and the original cap remains enforced. Cancellation releases a free follow-up; an initial visit with used follow-ups cannot be cancelled until those are resolved. Once the cap is reached, the next visit begins a new paid episode. Practitioner policy can inherit, enable or disable the hospital policy.

## Medication reminders

Preview the saved prescription calendar before sending. A duration of seven days with a two-day interval creates events on days 1, 3, 5 and 7. Events use the site's timezone and stable identifiers. Sending is an authorized POST action with a guard per saved prescription version and recipient. The delivery record distinguishes Queued, Sent and Failed; a queued response does not claim delivery. Failed queues can be refreshed/retried after correcting email configuration. A retry requires the prescription and recipient still to match. No message is sent by viewing a record.

## Inpatient care

Create one active admission per patient and choose an available bed. Transfers update both beds and ward occupancy in the same transaction. Patient/admission identity cannot be changed to reuse a clinical episode. Care entries derive their patient from the admission, record their author and validate chronology and nonnegative measurements. Finalize Discharge closes the admission, records the date/summary and releases the bed together. Reopening requires a reason and an available bed; a subsequent discharge requires a new summary. Keep clinical history instead of deleting admissions.

## Early departures

Visit/admission → Create → Record Departure records the outcome, actual time and reason separately from payment. Reception can finalize Left Before Seen only when no clinical work has started and cancellation dependencies permit closure. Other departures require a Doctor's assessment/advice. Visits become Closed Early while preserving findings, invoices, dispensing and fee history. Pending lab requests require an active named results owner and due date; the departure list exposes pending reviews, resolved only after all reports are Reviewed or Cancelled. New lab requests require a new active visit.

A Doctor can close an admission as Admission Cancelled before treatment, or record Transferred, Declined Further Care, Left During Care or Left Without Notice. Finalization releases the bed atomically without requiring a false condition or summary. Reopening with a reason retains the old departure record in history. Departure does not automatically credit charges, refund payments, return stock or prove patient consent/contact.

## Pharmacy

Map the prescribed Medicine to its Med Item. The doctor enters an approved dispense quantity separately from dosing instructions. Receive stock with batch, expiry, quantity, unit price and currency, then Save → Post Intake. Drafts do not affect stock. Posted intake creates lots and append-only movements. Choose available, unexpired lots, presented by earliest expiry; the pharmacist confirms the physical lot and selling price.

From a prescription, use Dispense Prescription → Add From Prescription to select a named medication, lot, quantity and selling price. The server rechecks patient, medicine mapping, approved remaining quantity, expiry and available stock at posting. A stock lot can appear once per dispensing record. Use separate records if one lot must serve multiple prescription rows. Saving a draft does not reserve stock; availability is checked again on Post Dispensing.

A posted sale creates an issued invoice and removes available stock for the sale. Record Handover records the actual recipient, date and supplied quantities; partial collections are capped against the remaining uncollected quantity. Historical sales remain Not Tracked. Record Return copies original lots/prices; choose Uncollected or Collected origin, actual quantity, reason and Quarantine/Restock disposition after inspection. Historical returns need Legacy Not Tracked. Returns default to quarantine and create a credit against the original invoice; a cash refund remains separate. Quarantine is unavailable for dispensing. Stock adjustments use Count Correction for signed available-stock changes, Release Quarantine for an inspected transfer to available stock, or Dispose Quarantine for removal. Release/disposal quantities are positive; expired lots cannot be released or handed over. Negative balances are rejected. Intake cancellation reverses its original receipt only if sufficient stock remains. Posted records are retained and corrected by returns/reversals.

## Billing and reconciliation

Consultation charges and pharmacy posting create source-linked invoices. Other inpatient/laboratory charges can be entered as explicit manual HMS Invoices. No automatic bed-day, service tariff or insurance calculation is implied. Review a draft, then Issue Invoice. Record Payment opens a receipt with an invoice allocation. Save, check the patient, currency, amount and allocations, then Post Payment. A receipt must be fully allocated to issued invoices of the same patient and currency; overpayment is rejected.

Create Credit reduces the charge. Record Refund references an original posted receipt and cannot exceed its unrefunded original allocation or the invoice's remaining net paid amount. A refund alone does not reduce the invoice charge; credit it when the charge is also being reversed. Source-linked invoices are cancelled or returned through their source transaction. Standalone unpaid/uncredited invoices can be voided with a reason. Posted receipts and issued invoice items cannot be edited or deleted.

Use HMS Reconciliation for invoices, credits, net allocated receipts, outstanding amounts and refund dues. Mixed currencies are not totalled together. Collection dashboards show gross recorded receipts before refunds; drafts are excluded. Historical unallocated receipts are visible separately in Accounts. Stock lots show the current balance and Stock Movements retain the quantity history. Concurrent transactions serialize shared resources; Frappe can return a retryable transaction conflict on contention. Refresh and retry an unposted operation after such a conflict; posting guards prevent duplicate movements/payments.

## Upgrade notes

Back up the database, public/private files and site configuration before schema changes. Existing stock documents become Legacy, retain their original values, and cannot be posted again. Establish verified physical opening balances in new intake records; no inventory movement is invented from old document totals. Existing receipts become Legacy Recorded and retain their original amount/date/payer. Allocate them explicitly to reviewed invoices before posting them into reconciliation. No historical invoice/payment match is guessed from a patient's display name.

Review older clinical records with missing associations or private attachments before editing them under the stricter validators. Existing fee windows, overlapping bookings or inconsistent historical bed allocations require explicit reconciliation; this release does not silently rewrite disputed clinical/financial history. Existing site custom permissions should also be reviewed against the role contract above.

## Regression checks

Use a disposable local site containing only Frappe and HMS, with the scheduler disabled and no outgoing provider. Never run fixture tests against operational records.

```sh
bench new-site hms-workflow-test.localhost
bench --site hms-workflow-test.localhost install-app hms
bench --site hms-workflow-test.localhost set-config allow_tests true
bench --site hms-workflow-test.localhost execute hms.tests.test_workflows.run
```

The test runner refuses other site names. Tests use reserved `.invalid` recipients and mock mail delivery. Concurrency cases commit example fixtures so independent database connections can test locking; these fixtures remain on the disposable site. The suite covers positive role journeys, negative permissions, booking conflicts, entitlement accounting, clinical associations, bed/discharge transitions, stock and payment posting, refunds, returns and partial-failure rollback. Provider delivery, mail-client calendar import and production load remain separate acceptance checks. The user guide delivery plan is in `USER-GUIDE-PLAN.md`.
