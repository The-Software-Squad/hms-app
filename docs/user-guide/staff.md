# Configure staff, doctors and schedules

Link a doctor to a staff account and working hours.

**Who can do this:** System Manager

[All workflows](README.md)

## What this workflow does

A Healthcare Practitioner links an Employee to an enabled User with the Doctor role. Schedules define when appointments can be booked; active records alone do not create availability.

## Before you start

- A staff User with the Doctor role; Employee and Department Type records.

## 1. Link the employee

Open Employee, select User on the Employee record and the department, and keep the employee Active. Save the staff record. HR fields remain restricted to administrators.

## 2. Create the practitioner

Open Healthcare Practitioner and select the Employee and department. The name and user are derived from that employee. Enable Active and save.

## 3. Set follow-up policy

Choose Inherit, Enabled or Disabled. Enabled uses the practitioner’s positive validity days and free-visit cap; Inherit follows Hospital Settings.

## 4. Enter availability

Create a Practitioner Schedule for that practitioner. Add weekday start/end slots and any effective date range, then save.

## 5. Try a booking

Book a slot fully inside a saved shift. Positive, non-overlapping windows are required. An inactive employee or disabled/non-Doctor user cannot serve as an active practitioner.

## What success looks like

The practitioner shows the correct linked User and appointments fit the intended shift.

## Common problems and recovery

Do not change a practitioner link to substitute another doctor in historical visits. Reception can manage scheduling only where permissions allow it. Hospital settings, practitioner setup, schedules and admissions now retain change history. Use Departments for clinical configuration; Medical departments and Patient care types are legacy reference lists.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Book or reschedule an appointment](booking.md)
- [Understand free follow-up eligibility](eligibility.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
