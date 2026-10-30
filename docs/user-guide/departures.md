# Record a patient leaving before care is finished

Record the actual departure, preserve work already done and assign pending results.

**Who can do this:** Receptionist · Doctor · System Manager

[All workflows](README.md)

## What this workflow does

A departure is separate from clinical completion and financial settlement. The care record keeps a readable link to the finalized departure; payment, credits, medicine returns and follow-up remain explicit actions.

## Before you start

- A saved active consultation or admission. Clinical departures require Doctor access.

## 1. Confirm the care record

Open the correct Patient Visit or IP Record and choose Create → Record Departure. Verify the patient and care record before recording what happened.

## 2. Select the observed outcome

For a visit without clinical work choose Left Before Seen; Reception can finalize it only after unresolved labs, posted medicines and consultation charges are resolved by their existing cancellation rules. For other departures a Doctor selects Left During Care, Declined Further Care, Transferred or Left Without Notice. For an admission that never started treatment use Admission Cancelled.

## 3. Record the time, reason and clinical advice

Enter Departed On and Reason. A Doctor records the assessment, advice, destination or referral details that are known in Clinical Notes. Do not imply that consent, handover or advice was received if the patient left without notice.

## 4. Assign unfinished lab work

When a visit has unresolved lab requests, enter an active Pending Results Owner and Results Review Due. Finalization is blocked without both. Review received results and cancel only requests that did not proceed; a departure does not erase lab history.

## 5. Finalize and verify

Save, review, then Finalize Departure. Left Before Seen uses cancellation. Other visits become Closed Early and retain existing findings, bills and dispensing. Admissions become Discharged with the departure outcome and release their bed atomically. No discharge summary or recovery condition is invented.

## 6. Reconcile and continue follow-up

Arrange credits/refunds, uncollected medicine reversals or collected returns separately. Clinical staff use the departure list filtered to Pending reviews and Resolve Results Review only after every linked lab request is Reviewed or Cancelled. Book a new appointment/visit if the patient returns; reopening an admission requires a reason and an available bed.

## What success looks like

The departure has the correct outcome/time/actor, the care record links to it, inpatient bed occupancy is released, and any unresolved lab work remains visibly assigned.

## Common problems and recovery

A finalized departure cannot be overwritten. Add a comment for later context; closed clinical notes require a new correction reason. A failed finalization leaves the care record and bed unchanged. Leaving does not mean the bill is settled or the prescribed medicines were collected.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Record a consultation and corrections](consultation.md)
- [Request, receive and review a lab report](labs.md)
- [Finalize discharge or reopen admission](discharge.md)
- [Dispense, hand over and return medicines](dispense.md)
- [Issue invoices, record payments and refunds](billing.md)

Written instructions source reviewed 22 October 2026. Source reviewed and server integration cases added; full role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
