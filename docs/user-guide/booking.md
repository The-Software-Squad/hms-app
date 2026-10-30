# Book or reschedule an appointment

Reserve a valid slot with the right doctor and department.

**Who can do this:** Receptionist · System Manager

[All workflows](README.md)

## What this workflow does

Appointments check practitioner availability and overlapping reservations. Before check-in an appointment can be rescheduled; after a visit is linked, cancel and rebook to preserve the episode identity.

## Before you start

- An active patient and practitioner with a saved Practitioner Schedule.

## 1. Start from the patient

Open the patient and choose Create → Book Appointment. Confirm the Patient and Practitioner.

## 2. Enter the slot

Set Appointment Date, Start Time, End Time and Department. The server fills an omitted end with 30 minutes, but the entire slot must still fit the shift.

## 3. Save the booking

Keep Status Scheduled and save. Availability and overlapping appointments are checked again on the server.

## 4. Reschedule before check-in

For an unlinked scheduled booking, edit the date/time and save. Choose another slot if a conflict appears.

## 5. Cancel and rebook when necessary

After check-in, consultation progress sets In Service and Completed automatically; reception cannot mark clinical completion or a no-show. Resolve linked lab requests, dispensing and financial balances before cancelling an unused episode, then create a new appointment when needed.

## What success looks like

The saved Scheduled appointment identifies the intended patient, doctor, department and complete time interval.

## Common problems and recovery

For an out-of-shift or overlap error, refresh the schedule and choose an available slot. A concurrent request can receive a retryable transaction conflict; refresh before retrying.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Check in a booked or walk-in patient](check-in.md)
- [Configure staff, doctors and schedules](staff.md)
- [Manage clinical follow-ups](follow-ups.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
