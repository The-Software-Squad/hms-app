# Reconcile records after an upgrade

Establish reviewed opening stock and allocate historical receipts.

**Who can do this:** System Manager

[All workflows](README.md)

## What this workflow does

An upgrade retains historical documents without inventing inventory movements or invoice/payment matches. Legacy statuses distinguish that retained history from the new posting ledger.

## Before you start

- A verified site backup; administrator and pharmacy/billing review.

## 1. Keep the backup

Before schema changes retain the site database, public/private files and site configuration according to your normal backup process.

## 2. Review Legacy stock

Old intake/dispensing documents remain Legacy and cannot be posted again. Compare them with the physical count and retained supplier/sales evidence.

## 3. Establish opening stock

Create reviewed new intake records for verified opening batches and quantities, then post them. Do not post an old receipt a second time or assume old totals equal current stock.

## 4. Allocate Legacy Recorded receipts

Old receipts keep their amount, date and payer. Review the correct invoices, enter full allocations and choose Post Payment to include them in reconciled balances.

## 5. Resolve historical ambiguity explicitly

Review missing clinical associations, overlapping bookings, bed state, fee windows, private attachments and site custom permissions. Preserve disputed history until an administrator resolves it. Historical posted sales have no proven collection history: do not invent recipients or handover dates. Use Legacy Not Tracked with a documented return origin/reason if a physical return is accepted. Medical Department and Patient Care Type are retained for compatibility but removed from the current sidebar; use Department Type for department setup.

## What success looks like

Opening lots have an explicit reviewed source and historical receipts are either clearly unallocated or explicitly reconciled.

## Common problems and recovery

Never match a patient or invoice only by display name. Some older records need human review under the stricter validators; do not bypass them with direct balance edits.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Receive medicines and inspect stock lots](intake.md)
- [Issue invoices, record payments and refunds](billing.md)
- [Read dashboards and investigate discrepancies](reporting.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
