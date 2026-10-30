# Dispense, hand over and return medicines

Track posted stock, actual handovers and inspected returns separately.

**Who can do this:** Pharmacist · System Manager

[All workflows](README.md)

## What this workflow does

Post Dispensing removes available stock and creates a charge. Record Handover separately records the recipient and actual quantity supplied. A return creates a credit; the pharmacist chooses quarantine or restock after checking the medicines. Cash refunds remain separate.

## Before you start

- Posted stock; Medicine mapped to Med Item; doctor-approved dispense Quantity for a prescription.

## 1. Start from the prescription

On a saved Prescription Given or Completed visit choose Create → Dispense Prescription. Confirm Patient and Patient Visit.

## 2. Add From Prescription

Choose Add From Prescription, select the named medicine, choose an available unexpired Stock Lot, enter Quantity and Selling Unit Price, then choose Add Item. Review the earliest expiry before selecting a physical lot.

## 3. Save and post

Save the Meds Out draft, check Currency and the rows, then choose Post Dispensing and confirm. Drafts do not reserve stock; posting rechecks available and approved quantities.

## 4. Review the result

The record is Posted, stock decreases and Invoice links to the issued charge. Record Payment is a separate action.

## 5. Record the actual handover

On a posted sale choose Record Handover. Confirm the remaining lots, enter Recipient Name and Collected On, and reduce quantities to those actually supplied. Save, then Post Handover. Repeat for a partial collection; Collection Status shows Not Collected, Partly Collected, Collected or Returned. Posting a sale does not prove a handover.

## 6. Record an uncollected reversal or collected return

On the posted sale choose Record Return. Keep the original customer, lot, price and prescription reference. Enter only actual quantities, choose Return Origin Uncollected or Collected and enter Return Reason. The selected origin is capped against the matching collection history. Historical sales without handover tracking require Legacy Not Tracked.

## 7. Inspect and choose the stock destination

Return Disposition defaults to Quarantine. Quarantined stock cannot be sold or handed out as available inventory. Choose Restock only after the pharmacist verifies the pack and applicable storage/expiry requirements; expired returns must remain quarantined. Save and Post Dispensing to record the return and invoice credit. Refund money separately when required.

## 8. Release or dispose quarantined medicines

Use a Stock Adjustment with Release Quarantine or Dispose Quarantine, a positive quantity and an inspection/disposal reason. Release moves the same quantity from quarantine to available stock; disposal removes it from quarantine. An expired lot cannot be released.

## What success looks like

The sale has the correct charge, handover records identify the recipient and quantities actually supplied, and returns credit only eligible quantities into the selected stock bucket.

## Common problems and recovery

Expired or insufficient stock, an unmapped medicine or an exceeded approved quantity blocks posting. A medicine already used by prescriptions cannot be remapped to a different pharmacy item; ask the appropriate clinical staff to create a new medicine and correct the prescription. One lot can appear once per record; use separate records if the same lot serves multiple prescription rows. Stock removed by posting is held for this sale until handover or an explicit uncollected return. A collected return does not create another handover allowance on the same sale; use a new approved dispensing record for a replacement.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Receive medicines and inspect stock lots](intake.md)
- [Adjust stock with a reason](stock-adjustments.md)
- [Issue invoices, record payments and refunds](billing.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
