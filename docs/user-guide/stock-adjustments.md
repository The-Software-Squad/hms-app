# Adjust stock with a reason

Record a counted difference without erasing movements.

**Who can do this:** Pharmacist · System Manager

[All workflows](README.md)

## What this workflow does

Count Correction changes the available balance by a signed quantity. Release Quarantine transfers inspected units from quarantine to available stock; Dispose Quarantine removes units from quarantine. Every posting retains the reason, actor and movement history.

## Before you start

- A posted stock lot and a verified physical count/reason.

## 1. Inspect the lot

Open HMS Stock Lot and check item, batch, expiry, Available Quantity and Quarantined Quantity. Review Stock Movements and their Stock Bucket before deciding the correction.

## 2. Create the adjustment

Select Stock Lot and Adjustment Type. For Count Correction enter a positive quantity to add or negative to remove available stock. For Release Quarantine or Dispose Quarantine enter a positive quantity taken from the quarantine balance.

## 3. Explain the correction

Enter a specific Reason, such as a verified count difference or damaged units. A zero quantity or missing reason is rejected.

## 4. Save and Post Adjustment

Save, review the signed quantity, then choose Post Adjustment and confirm. Posting rechecks the current balance.

## 5. Review and reverse when needed

Check both lot balances and the matching movement bucket. A quarantine release creates equal negative quarantine and positive available movements. A disposal creates only a negative quarantine movement. Posted records are immutable; record any further correction explicitly with its actual reason.

## What success looks like

The lot balance changes by exactly the posted signed quantity, and the movement retains the source and actor.

## Common problems and recovery

Negative balances are rejected. An expired lot cannot be dispensed, handed over or released from quarantine. Count Correction does not release quarantine; use the explicit Release Quarantine action after inspection.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Receive medicines and inspect stock lots](intake.md)
- [Dispense, hand over and return medicines](dispense.md)
- [Read dashboards and investigate discrepancies](reporting.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
