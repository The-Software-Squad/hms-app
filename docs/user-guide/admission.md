# Admit, allocate a bed and transfer

Create one active admission and keep bed occupancy consistent.

**Who can do this:** Receptionist · System Manager

[All workflows](README.md)

## What this workflow does

An IP Record identifies the inpatient episode and its responsible practitioner. Saving an allocation or transfer updates the relevant beds and ward occupancy together.

## Before you start

- An active patient, practitioner and available Bed in a Ward.

## 1. Start the admission

On Patient choose Create → New Admission. Confirm Patient, Admission Date and Practitioner.

## 2. Choose an available bed

Select an available Bed and Status Admitted, then save. A bed is required before any admission can be saved. A patient can have only one active admission and another patient’s occupied bed cannot be selected.

## 3. Review occupancy

Open the Bed to verify Current Patient and Current Admission. Ward Total Occupied is maintained by admission changes.

## 4. Transfer within the same episode

On the active IP Record select another available Bed and save. The previous bed is released and the new bed is allocated in the same transaction.

## 5. Continue inpatient care

Use Create → Record Treatment for clinical care or Create → Discharge Summary when ready for discharge. Those actions require clinical permissions.

## What success looks like

The active admission owns exactly the selected bed and the previous bed is free after a transfer.

## Common problems and recovery

Do not edit bed occupancy directly or change an admission’s patient to reuse the record. An active-admission or occupied-bed conflict requires choosing the correct existing episode/available bed.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Record inpatient care and vitals](care.md)
- [Finalize discharge or reopen admission](discharge.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
