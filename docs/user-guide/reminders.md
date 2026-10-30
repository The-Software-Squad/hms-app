# Prescribe and send medication reminders

Preview a dated schedule and track its email queue.

**Who can do this:** Doctor · System Manager

[All workflows](README.md)

## What this workflow does

Medication Schedule produces a calendar attachment from saved dosing windows. Sending records a delivery request per prescription version and recipient; queued mail is different from successful delivery.

## Before you start

- A patient email; a saved Medicine Timing; a prescription in Prescription Given or Completed; outgoing email configured by an administrator for real sends.

## 1. Complete the prescription row

Select Medicine, Dose, Timing, start date and Duration (days). For pharmacy dispensing also enter an approved Quantity in the row’s expanded form.

## 2. Check the elapsed duration

Duration is the total calendar span. Seven days with a two-day interval gives events on days 1, 3, 5 and 7, using the site’s timezone.

## 3. Save and preview

Save the visit with Prescription Given or Completed, then choose Medication → Preview Medication Calendar. Review dates, times and medicine instructions.

## 4. Queue deliberately

Choose Medication → Send Medication Mail, review the confirmation and confirm the saved recipient. The delivery record opens; repeat clicks reuse the same request.

## 5. Check delivery or recover

Use Refresh Delivery Status on HMS Medication Delivery. Sent requires the queue’s sent status. For Failed, correct the outgoing-account issue and use Retry Failed Email; changed prescriptions or recipients need a new preview/send.

## What success looks like

The requested delivery has the expected patient, recipient, actor and status. A Queued response alone does not mean the email arrived.

## Common problems and recovery

No schedule, an invalid recipient or a missing outgoing queue must be corrected. The walkthrough previews the calendar and inspects delivery status without sending email.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Record a consultation and corrections](consultation.md)
- [Dispense, hand over and return medicines](dispense.md)

Written instructions source reviewed 19 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
