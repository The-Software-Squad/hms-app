# Issue invoices, record payments and refunds

Reconcile charges, credits, posted receipts and refund dues.

**Who can do this:** Receptionist · Pharmacist · System Manager

[All workflows](README.md)

## What this workflow does

Standalone HMS invoices and allocations track operational balances. They do not process money through a gateway or provide a general ledger, tax, insurance or automatic inpatient-tariff system.

## Before you start

- An issued source invoice or a reviewed manual charge; patient and currency confirmed.

## 1. Review or issue the invoice

Consultation and posted pharmacy actions create issued source invoices. For other charges create HMS Invoice with Patient/Payer, Date, Currency and Items, save and choose Issue Invoice.

## 2. Record Payment

On an invoice with an outstanding amount choose Record Payment. Check patient, amount, date, Payment Mode, Towards and Allocations. The full receipt must be allocated to issued invoices for the same patient/currency.

## 3. Post Payment

Save and review, then choose Post Payment and confirm. A draft does not count as payment. The server prevents overpayment and retains posted allocations.

## 4. Credit a reduced charge

Use Create Credit on the original invoice, review the amount and issue it. For returned medicines use Record Return on the dispensing source to keep stock and credit aligned.

## 5. Record Refund

On the original posted Receive receipt choose Record Refund. Adjust the amount/allocations to the actual refund, save and post. It cannot exceed the original unrefunded allocation or remaining paid balance.

## 6. Reconcile

Open HMS Reconciliation for credits, Net Receipts, Outstanding and Refund Due. A refund alone does not reduce the charge. A fully credited and fully refunded consultation can be cancelled while retaining its original invoice, credit and receipts. A partially credited consultation must have its remaining charge resolved before cancellation. Unpaid uncredited source charges are voided through their source; standalone invoices use Void Invoice with a reason.

## What success looks like

The invoice balance reflects issued credits and net posted allocated receipts; draft receipts are excluded.

## Common problems and recovery

Currency/patient mismatch, overpayment, excess credit or an excessive refund is rejected. Posted financial records cannot be edited or deleted; use the documented reversal path.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Dispense, hand over and return medicines](dispense.md)
- [Read dashboards and investigate discrepancies](reporting.md)
- [Reconcile records after an upgrade](legacy.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
