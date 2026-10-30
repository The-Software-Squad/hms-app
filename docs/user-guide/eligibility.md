# Understand free follow-up eligibility

Understand the allowed free visits and inclusive expiry date.

**Who can do this:** Receptionist · Doctor · System Manager

[All workflows](README.md)

## What this workflow does

Fee Validity links an initial paid consultation to a limited number of free follow-ups with the same practitioner. The cap counts free follow-ups, excluding the initial visit.

## Before you start

- Hospital Settings policy configured by a System Manager; any practitioner override reviewed.

## 1. Review the policy

Ask a System Manager to review Enable Free Follow-ups, Validity (Days) and Max Free Visits in Hospital Settings. Practitioners can have an Inherit, Enabled or Disabled Follow-up Policy. Reception and doctors can read Fee Validity; Hospital Settings is administrator-only.

## 2. Save the initial consultation

Check in or save a walk-in visit. When enabled it starts an eligibility window and creates the configured consultation charge; a zero fee produces no invoice.

## 3. Read the window

Open Fee Validity from the visit. Start Date is included: seven days means that date through six days later. Visits Completed counts the free follow-up references; Max number of free visits is the cap, excluding the initial visit.

## 4. Use a qualifying follow-up

Eligibility uses the actual Visit date, including when the visit is entered late. A visit inside the matching practitioner window consumes an unused free place even if that window is labelled Expired today. Cancelled windows never qualify. After the cap, the next visit starts a new paid episode.

## 5. Cancel in the right order

Cancelling a free follow-up releases its place. To cancel an initial visit with used follow-ups, resolve those linked visits first. Cancelled windows remain cancelled.

## What success looks like

The window dates, free references and cap explain why the consultation was charged or eligible.

## Common problems and recovery

The active-date range and remaining allowance must match the actual Visit date. Expired describes the window today; a historical visit may still qualify within its original dates. Cancelled windows cannot grant eligibility. Disabled policy creates normal consultation charges without a free window.

## Screenshots and walkthrough

Updated screenshots and a screen-recorded GIF are being prepared. The written steps are available below.

## Related workflows

- [Check in a booked or walk-in patient](check-in.md)
- [Issue invoices, record payments and refunds](billing.md)
- [Manage clinical follow-ups](follow-ups.md)

Written instructions source reviewed 22 October 2026. Source reviewed; full workflow and role-specific browser verification pending.

Examples follow Maya Patel, Dr Alex Morgan and Paracetamol 500 mg through the HMS workflows. Contact addresses use example domains; the reminder demonstration does not send email.
