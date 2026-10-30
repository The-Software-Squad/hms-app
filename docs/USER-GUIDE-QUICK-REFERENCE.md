# HMS staff quick reference

Written instructions source reviewed on 22 October 2026. Use the [full user guide](user-guide/README.md) for prerequisites, limits and recovery. Site-specific roles may narrow access further.

## Find a sidebar section

Select a section to expand its links. Overview and User guide are always at the top when your role permits access. Each section only shows links your roles allow.

| Section | What belongs here |
|---|---|
| Reception | Reception dashboard, patients, appointments, follow-ups and fee eligibility |
| Clinical Care | Doctor dashboard, consultations, lab reports, departures/pending reviews and medication reminders |
| Inpatient Care | Admissions, care and vitals, discharge summaries, wards and beds |
| Pharmacy | Pharmacy dashboard, stock intake, dispensing, handovers and returns, stock lots, movements, adjustments, medicines, stock items and suppliers |
| Accounts | Accounts dashboard, invoices and credits, payments and refunds |
| Reports | Analytics and HMS reconciliation |
| Administration | Hospital settings, staff, practitioners, schedules, reference lists and patient merge history |

The sidebar uses friendly labels: **Stock intake** opens Meds In take, **Dispensing and returns** opens Meds Out, and **Payments and refunds** opens Payment Recipit. Form and list titles use the same readable terminology. Stored record types and references remain intact; native breadcrumbs or Desk search may still show the older technical DocType names.

## Hospital Live · 3D

Open Hospital Live · 3D from the sidebar to inspect doctor rooms, grouped waiting seats and saved care activity. Characters follow HMS actions; camera movement does not change care. Configure rooms/seats in Hospital Settings. Doctors report their own availability from their room. See [the simulation guide](user-guide/hospital-live.md).

## Choose the next task

| Starting point | Next action | Evidence to check |
|---|---|---|
| Patient arrives for the first time | Search Patient; create a record only when needed | Patient ID, name and verified contact details |
| Existing patient needs an appointment | Patient → Create → Book Appointment | Saved Scheduled slot inside practitioner availability |
| Booked patient arrives | Appointment → Check In | Checked In and one linked Patient Visit |
| Walk-in arrives | Patient → Create → New Walk-in Visit | Correct Patient, Doctor, Department and Visit date |
| Doctor records care | Patient Visit → findings, prescription and Status | Saved findings; review pending lab work before Completed |
| Lab result arrives | Lab Report → private Report File, Received On, Received | Patient/visit match; a Doctor saves Reviewed |
| Medication reminder is needed | Save visit → Medication → Preview Medication Calendar | Correct recipient, dates and times before Send Medication Mail |
| Clinical follow-up is due | Follow-ups → due visit | Pending/Contacted queue; save contact notes separately from booking |
| Patient needs admission | Patient → Create → New Admission | One active IP Record and an available Bed |
| Inpatient care is recorded | IP Record → Create → Record Treatment | Correct In Patient, Treating Doctor, date, values and units |
| Patient is ready to leave | Discharge Summary → save Draft → Finalize Discharge | Admission Discharged and bed released |
| Pharmacy receives stock | Meds In take → save Draft → Post Intake | Posted intake and available stock lot |
| Pharmacy supplies a prescription | Meds Out → Add From Prescription → save → Post Dispensing | Posted sale, stock movement and issued invoice |
| Medicines are handed over | Posted sale → Record Handover → Post Handover | Recipient and actual supplied quantities; partial collections tracked |
| Medicines come back or remain uncollected | Original Posted sale → Record Return | Correct origin, inspected disposition, eligible quantity and credit |
| Patient leaves before care is finished | Visit/admission → Create → Record Departure → Finalize Departure | Actual outcome; pending results assigned; inpatient bed released |
| Quarantine needs resolution | Stock Adjustment → Release Quarantine / Dispose Quarantine | Positive quantity, reason and matching stock bucket movements |
| Physical count differs | HMS Stock Adjustment → signed quantity + Reason → Post Adjustment | Matching movement and new lot quantity |
| Money is received | Invoice → Record Payment → review allocations → Post Payment | Posted allocated receipt; invoice balance updated |
| Charge or payment needs reversal | Original invoice → Create Credit; original receipt → Record Refund | Credit reduces charge; refund reduces net receipts |
| Totals disagree | Check source/status/date/currency, then HMS Reconciliation or stock movement | Explain the total from its underlying records |

## Read record states correctly

| State | Meaning for staff |
|---|---|
| Not Saved | Edits are still in the form. A button click or failed save does not record the change. |
| Draft intake, dispensing, adjustment or receipt | Saved preparation; stock or payment posting has not occurred. Draft stock transactions do not reserve stock. |
| Posted | Stock/payment action has taken effect. Correct it through its reversal workflow. |
| Issued invoice or credit | Charge or reduction is included in invoice balances. |
| Queued medication delivery | Awaiting delivery. It is not proof the email was sent. |
| Sent medication delivery | The linked email queue reports sent; confirm status with Refresh Delivery Status. |
| Closed Early visit | Patient left before care finished; recorded findings, bills and assigned pending results remain. |
| Quarantined stock | Held outside the available balance until explicitly released or disposed by a pharmacist. |
| Completed visit | Findings were finalized; clinical amendments and Follow up date changes require a new Correction Reason. |
| Draft discharge | The patient remains admitted and the bed is still allocated. |
| Finalized discharge | Admission and bed release were updated together. |
| Legacy stock / Legacy Recorded receipt | Retained historical data needs explicit opening-stock or allocation review. |

## Role boundaries

| Role | Typical responsibilities | Boundary |
|---|---|---|
| Receptionist | Demographics, scheduling, check-in, admissions, follow-up progress, receipts and reconciliation | Cannot review lab results or edit clinical findings/prescriptions. Hospital Settings is administrator-only. |
| Doctor | Demographics, consultation, lab review, medication preview/send, inpatient care and discharge | Doctor-only access does not include HMS Reconciliation or pharmacy stock management. |
| Pharmacist | Stock receipt, dispensing, returns, adjustments, invoice/payment work and reconciliation | Prescriptions remain the doctor’s approved clinical instructions. Clinical notes and HR details are restricted. |
| System Manager | Staff/practitioner setup, hospital policy, duplicate merges, historical reconciliation and administration | A shared name/phone does not establish duplicate identity; retain reviewed reasons and audit evidence. |

Role filters in the guide describe responsibilities; they do not grant permissions. Some chapters contain steps handed over between staff roles.

## If a step fails

1. Read the validation message and check whether **Not Saved** remains. Keep the record ID and the exact message.
2. After a conflict or interrupted posting, refresh the source before retrying. Check for an existing linked visit, movement, invoice or delivery.
3. Correct the supplied data or ask the responsible staff role to complete the step. Avoid changing derived balances or assigning generated links manually.
4. Changes to clinical content or the Follow up date on a Completed or Closed Early visit require clinical review and a new Correction Reason. Saving contact notes alone does not amend those fields.
5. If the discrepancy remains, give your System Manager the record ID, action and error through your hospital’s approved support process.

Clinical follow-up dates and free-fee eligibility are separate. A refund and a credit are separate. Recorded Receipts is a gross historical collection view; use HMS Reconciliation for allocated net receipts, credits, outstanding amounts and refund dues.

## Updated workflow rules

- Appointment In Service/Completed follows the consultation; reception cannot set clinical completion or mark an arrived patient No Show.
- Resolve lab work and any unreturned posted medicines before cancellation. Fully credited and fully refunded consultation invoices are retained; an unpaid uncredited source charge is voided.
- Free-follow-up eligibility uses the actual visit date, including late entry. Cancelled windows never qualify and the original cap still applies.
- A bed is required before any admission can be saved.
- Medicines already referenced by prescriptions cannot be renamed or have their identity/pharmacy mapping changed. Create a new catalogue entry and correct the prescription.

- Finalized departure records preserve the actual disposition separately from billing. Follow pending lab reviews from Clinical Care → Departures and pending reviews.
- A posted sale is not proof of collection. Historical sales remain Not Tracked, with no invented handover.
- Collected returns default to quarantine; restocking requires an explicit pharmacist decision after inspection. Expired medicines cannot be released.
