# Finalize discharge or reopen admission

Finalize the summary and release the bed together.

**Who can do this:** Doctor · System Manager

[All workflows](README.md)

## What this workflow does

A discharge draft is a clinical document in progress. Finalize Discharge closes the admission, links the summary and releases the bed in one transaction.

## Before you start

- An active admission and a saved draft Discharge Summary; Doctor access.

## 1. Prepare the summary

On IP Record choose Create → Discharge Summary. Verify the patient, admission and Practitioner; enter Discharge Date, Final Diagnosis, Discharge Notes, Condition at Discharge and any Follow Up.

## 2. Save the draft

Save and review the summary. Saving a Draft does not discharge the patient or free the bed.

## 3. Finalize deliberately

Choose Finalize Discharge and confirm. This records the actor/date, changes IP Record to Discharged and releases the bed together.

## 4. Check the result

Open the admission and bed to confirm the discharge link/date and released allocation. Review the patient follow-up date when provided.

## 5. Record a different departure

For transfer, refusal of further care or leaving without notice, open the admission and choose Create → Record Departure. A Doctor records the actual outcome, time, reason and assessment/advice, then Finalize Departure releases the bed. Admission Cancelled is allowed only before treatment starts.

## 6. Reopen only when appropriate

Use Actions → Reopen Admission with a reason. The selected bed must be available. A subsequent discharge needs a new summary; finalized summary corrections require a new Correction Reason.

## What success looks like

The summary is Finalized, the admission is Discharged and the bed is available.

## Common problems and recovery

If the transaction fails, refresh both records before retrying. Do not manually set Discharged or overwrite a completed summary to represent a new discharge.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Admit, allocate a bed and transfer](admission.md)
- [Record inpatient care and vitals](care.md)
- [Manage clinical follow-ups](follow-ups.md)
- [Record a patient leaving before care is finished](departures.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
