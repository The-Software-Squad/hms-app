# Record inpatient care and vitals

Add dated care and measurements to the right admission.

**Who can do this:** Doctor · System Manager

[All workflows](README.md)

## What this workflow does

In Patient Treatment belongs to one admission and derives its patient from that episode. It records who entered the care and vitals; measurements must be checked with the displayed units.

## Before you start

- An IP Record; Doctor access and verified observations.

## 1. Start from the admission

Open the active IP Record and choose Create → Record Treatment. Check In Patient, the derived Patient and Treating Doctor.

## 2. Enter dated care

Choose the Date and enter Medications Given and Diagnosis Update. The date must be between admission and today and cannot be after discharge.

## 3. Add vitals

Add each Vitals row, choose its Time and enter the observed values using the field’s displayed units. Expand the row for fields not visible in the grid.

## 4. Save and review

Save the treatment. Recorded By and new vital authors come from the logged-in account. Use View → Treatment History on IP Record for the list, or Previous Treatments → Load treatment history / Load more on a treatment to review earlier entries.

## 5. Correct transparently

Keep the historical record and make a documented correction using your hospital’s correction process and version history. Do not delete the episode’s care history.

## What success looks like

The saved care entry belongs to the intended admission and patient, has a valid date and shows the actual recording user.

## Common problems and recovery

Contradictory patient/admission associations, dates outside the episode or negative measurements are rejected. Verify units and observations rather than bypassing validation.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Admit, allocate a bed and transfer](admission.md)
- [Finalize discharge or reopen admission](discharge.md)

Written instructions source reviewed 19 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
