# Receive medicines and inspect stock lots

Post received batches before they become available stock.

**Who can do this:** Pharmacist · System Manager

[All workflows](README.md)

## What this workflow does

Meds In take records supplier receipt details. Stock changes only through Post Intake, which creates traceable lots and append-only movements.

## Before you start

- Meds Provider and Med Item records; verified batch, expiry, quantity, cost and currency.

## 1. Enter the receipt

Open Meds In take and create a record. Select Provider, Date, supplier Invoice Number and Currency.

## 2. Add batch rows

For each row select Medical Item Name and enter Batch Number, Count, Expires At and Single Item Price. Expand rows for the full fields.

## 3. Review totals and save

Review the calculated Price, Discount and Total, then save. Draft available stock remains zero.

## 4. Post Intake

Choose Post Intake and confirm. Only nonexpired, valid quantities can be posted. Posting again reuses the posted record.

## 5. Inspect the lot and history

Open the row’s Stock Lot or HMS Stock Lot list. Check item, batch, expiry, currency and Available Quantity; use HMS Stock Movement for its history. Cancel Intake requires a reason and enough remaining stock to reverse the original receipt.

## What success looks like

The intake is Posted and the new lot has the received quantity and a Stock received movement.

## Common problems and recovery

Posted rows cannot be edited to change stock. Use a return/reversing adjustment as appropriate. Legacy intake is read-only and cannot establish opening stock automatically.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Dispense, hand over and return medicines](dispense.md)
- [Adjust stock with a reason](stock-adjustments.md)
- [Reconcile records after an upgrade](legacy.md)

Written instructions source reviewed 19 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
