# Record a consultation and corrections

Review history, record findings and complete the visit.

**Who can do this:** Doctor · System Manager

[All workflows](README.md)

## What this workflow does

The consultation records clinical findings, prescriptions and follow-up plans. Completion keeps an actor and date, while later corrections require a new reason and preserve history.

## Before you start

- A checked-in Patient Visit; Doctor access.

## 1. Confirm the episode

Open the visit and verify Patient, Doctor, Department and Visit date. In Previous Visits use Load previous visits, then Load more when offered, to review available history.

## 2. Record findings

Set the consultation status as work progresses and enter Remarks. Use Medication Details for additional instructions and Medication Schedule for timed prescriptions.

## 3. Resolve laboratory work

Use Create → Request Lab Report during an active consultation. Review or cancel each pending report before completing or cancelling the consultation. Closed consultations cannot accept new lab requests; create a new visit for further care.

## 4. Plan the follow-up

Enter Follow up, Follow Up Status and any outreach notes. This clinical date is independent of the fee-validity expiry.

## 5. Record leaving before care is finished

If the patient leaves, choose Create → Record Departure and describe the actual outcome. Left Before Seen is for a visit without clinical work. Clinical staff close other departures as Closed Early, with assessment/advice and an owner/due date for unresolved lab results.

## 6. Complete or correct

Set Status Completed after recording findings and save. To amend completed clinical content or the Follow up date, enter a new Correction Reason before saving the revised record. Confirm that the saved status appears and Not Saved clears.

## What success looks like

The completed visit retains its findings, completion actor/date and linked reports. Patient/doctor/date identity is unchanged.

## Common problems and recovery

A missing-findings or pending-lab error explains what remains. Completed or cancelled visits cannot be reopened as a new consultation. Medicines already used in prescriptions cannot have their identity or pharmacy item changed; create a new catalogue entry and amend a completed prescription with a new Correction Reason. Closed Early visits also require a new Correction Reason for clinical amendments and cannot be reopened. Their invoices and dispensing history remain for separate reconciliation.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Request, receive and review a lab report](labs.md)
- [Prescribe and send medication reminders](reminders.md)
- [Manage clinical follow-ups](follow-ups.md)
- [Record a patient leaving before care is finished](departures.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
