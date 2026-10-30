# Request, receive and review a lab report

Keep an uploaded result attached to its own patient and visit.

**Who can do this:** Receptionist · Doctor · System Manager

[All workflows](README.md)

## What this workflow does

Lab Report tracks Requested, Received, Reviewed or Cancelled states for a private uploaded report. It does not connect to a laboratory instrument or external results service.

## Before you start

- A saved visit; a configured Lab Report Type; a private report file when receiving.

## 1. Request from the visit

A Doctor or System Manager opens Patient Visit and chooses Create → Request Lab Report. Select Report Type and Requested On, then save. Patient is derived from the visit. Reception can manage the report through its permitted forms; the visit shortcut is clinical-only.

## 2. Receive the file

Open the same report. Upload the report through Report File with private storage, enter Received On and set Status Received. Save the record.

## 3. Review clinically

A Doctor opens the correct patient/visit and file, records the review by setting Status Reviewed, and saves. Reception cannot mark a clinical review.

## 4. Resolve a request that will not proceed

Set an unreviewed request to Cancelled when appropriate, retaining the reason in the available record notes/comments according to your local process.

## 5. Complete the consultation

Return to the visit after all reports are Reviewed or Cancelled. A reviewed report’s file and review details are retained.

## 6. Track results after a departure

For a patient who left during care, open Clinical Care → Departures and pending reviews and filter Pending Results Review to Pending. Review or cancel the linked requests as appropriate, then a Doctor uses Resolve Results Review on the departure. Leaving does not cancel a received result or count as clinical review.

## What success looks like

The result belongs to the right visit/patient, downloads with permission, and shows the review actor/date.

## Common problems and recovery

Public/external URLs and files belonging to another report are rejected. Upload the correct private file instead. Received/Reviewed requires both a file and a received date.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Record a consultation and corrections](consultation.md)
- [Prescribe and send medication reminders](reminders.md)
- [Record a patient leaving before care is finished](departures.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
