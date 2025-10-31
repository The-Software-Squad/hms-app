# -*- coding: utf-8 -*-
# Copyright (c) 2025
# For license information, please see license.txt

import datetime
import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class FeeValidity(Document):
    def validate(self):
        self.update_status()

    def update_status(self):
        today = getdate(nowdate())
        if self.valid_till and getdate(self.valid_till) < today:
            self.status = "Expired"
        elif (self.max_visits or 0) and (self.visited or 0) >= int(self.max_visits):
            self.status = "Completed"
        else:
            self.status = "Active"


def _get_validity_settings(practitioner=None):
    settings = frappe.get_single("Hospital Settings")
    valid_days = int(settings.get("valid_days") or 1)
    max_visits = int(settings.get("max_visits") or 1)
    enabled = int(settings.get("enable_free_follow_ups") or 0) == 1

    if practitioner:
        try:
            doc = frappe.get_cached_value(
                "Healthcare Practitioner",
                practitioner,
                ["enable_free_follow_ups", "valid_days", "max_visits"],
                as_dict=True,
            )
            if doc and (doc.enable_free_follow_ups or enabled):
                enabled = True
                valid_days = int(doc.valid_days or valid_days)
                max_visits = int(doc.max_visits or max_visits)
        except Exception:
            pass
    return enabled, valid_days, max_visits


def _patient_has_active_validity(patient, practitioner, date):
    return frappe.db.exists(
        "Fee Validity",
        {
            "patient": patient,
            "practitioner": practitioner,
            "status": ["in", ["Active"]],
            "start_date": ["<=", date],
            "valid_till": [">=", date],
        },
    )


def create_fee_validity_from_visit(visit):
    """Create a Fee Validity starting from this Patient Visit and link it back to the visit.

    Always creates a validity window (using Hospital/Practitioner settings for days/visits),
    if no overlapping active validity exists for this patient + practitioner.
    """
    # In HMS, Patient Visit.doctor links to Healthcare Practitioner
    _enabled, valid_days, max_visits = _get_validity_settings(visit.get("doctor"))
    practitioner_link = visit.get("doctor")

    # Prevent duplicates
    if practitioner_link and _patient_has_active_validity(visit.patient, practitioner_link, visit.visit_date):
        return None

    fee_validity = frappe.new_doc("Fee Validity")
    fee_validity.practitioner = practitioner_link
    fee_validity.patient = visit.patient
    fee_validity.department = visit.department
    fee_validity.patient_visit = visit.name
    fee_validity.max_visits = max_visits or 1
    fee_validity.visited = 0
    fee_validity.start_date = getdate(visit.visit_date)
    fee_validity.valid_till = getdate(visit.visit_date) + datetime.timedelta(days=int(valid_days or 1))
    fee_validity.save(ignore_permissions=True)
    try:
        frappe.db.set_value("Patient Visit", visit.name, "fee_validity", fee_validity.name)
    except Exception:
        pass
    try:
        _ensure_fee_validity_invoice(fee_validity)
    except Exception as e:
        frappe.log_error(f"Failed to create invoice for Fee Validity {fee_validity.name}: {e}", "HMS Fee Validity")
    return fee_validity


def manage_fee_validity_on_visit(doc, method=None):
    """Doc Event: called on Patient Visit after insert.

    - If no active validity exists and follow-ups enabled: create one from this visit.
    - Else if active validity exists and this visit is not the initial linked visit: increment visited and add reference.
    """
    if not (doc.patient and doc.visit_date):
        return

    # Practitioner is a Healthcare Practitioner link on Patient Visit
    practitioner_link = doc.get("doctor") if doc.get("doctor") else None

    _enabled, valid_days, max_visits = _get_validity_settings(practitioner_link)

    # Check existing active validity for this date
    filters = {
        "patient": doc.patient,
        "start_date": ("<=", doc.visit_date),
        "valid_till": (">=", doc.visit_date),
    }
    if practitioner_link:
        filters["practitioner"] = practitioner_link

    validity_name = frappe.db.exists("Fee Validity", filters)

    if not validity_name:
        # Create new validity window from this visit
        fee_validity = create_fee_validity_from_visit(doc)
        return

    # Update existing validity: add this visit if not the initial
    fee_validity = frappe.get_doc("Fee Validity", validity_name)
    # If this is the initial visit, just ensure link is set on visit
    if fee_validity.patient_visit == doc.name:
        try:
            frappe.db.set_value("Patient Visit", doc.name, "fee_validity", fee_validity.name)
        except Exception:
            pass
        return

    # Avoid duplicates in child table
    exists = frappe.db.exists("Fee Validity Reference", {"visit": doc.name})
    if exists:
        try:
            frappe.db.set_value("Patient Visit", doc.name, "fee_validity", fee_validity.name)
        except Exception:
            pass
        return

    # Only increment if validity still active
    fee_validity.append("ref_visits", {"visit": doc.name})
    fee_validity.visited = int(fee_validity.visited or 0) + 1
    fee_validity.update_status()
    fee_validity.save(ignore_permissions=True)
    try:
        frappe.db.set_value("Patient Visit", doc.name, "fee_validity", fee_validity.name)
    except Exception:
        pass


def _ensure_fee_validity_invoice(fv: Document):
    """Create a Sales Invoice for the given Fee Validity if not already linked.

    Uses Hospital Settings for item name and rate. Creates a Customer if none exists for the Patient.
    """
    if fv.get("sales_invoice_ref"):
        return fv.get("sales_invoice_ref")

    settings = frappe.get_single("Hospital Settings")

    # Resolve company
    company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")

    # Resolve patient and customer
    patient = fv.get("patient")
    if not patient:
        return None
    customer = None
    try:
        # Use linked customer if Patient has the field
        cust_field = frappe.get_meta("Patient").has_field("customer")
        if cust_field:
            customer = frappe.db.get_value("Patient", patient, "customer")
    except Exception:
        pass
    if not customer:
        # Create minimal Customer
        p_doc = frappe.get_doc("Patient", patient)
        customer = _ensure_customer_for_patient(p_doc, settings)

    # Resolve item and income account
    item_name = settings.get("fee_validity_item_name") or "Fee Validity"
    rate = settings.get("fee_validity_rate") or 0

    income_account = None
    if company:
        income_account = frappe.db.get_value("Company", company, "default_income_account")
    if not income_account:
        income_account = settings.get("default_income_account")
    if not income_account and company:
        acc = frappe.get_all("Account", filters={"company": company, "root_type": "Income", "is_group": 0}, fields=["name"], limit=1)
        income_account = acc[0].name if acc else None

    # UOM
    uom = frappe.db.exists("UOM", "Nos") or frappe.db.get_single_value("Stock Settings", "stock_uom") or "Nos"

    inv = frappe.new_doc("Sales Invoice")
    inv.customer = customer
    if company:
        inv.company = company
    inv.due_date = getdate()
    inv.posting_date = getdate()
    inv.is_pos = 0

    row = inv.append("items")
    # Ideally use an Item, but fallback to free-form row
    row.item_name = item_name
    row.description = f"Fee Validity for Patient {patient}"
    row.qty = 1
    row.uom = uom
    row.conversion_factor = 1
    row.rate = rate
    row.amount = rate
    if income_account:
        row.income_account = income_account

    inv.set_missing_values()
    inv.save(ignore_permissions=True)

    frappe.db.set_value("Fee Validity", fv.name, "sales_invoice_ref", inv.name)
    return inv.name


def _ensure_customer_for_patient(p_doc: Document, settings: Document) -> str:
    # Try to find existing by name
    existing = frappe.get_all("Customer", filters={"customer_name": p_doc.patient_name}, pluck="name", limit=1)
    if existing:
        cust_name = existing[0]
    else:
        # Defaults
        from frappe.utils.nestedset import get_root_of

        customer_group = getattr(p_doc, "customer_group", None) or settings.get("default_customer_group") or get_root_of("Customer Group") or "All Customer Groups"
        territory = getattr(p_doc, "territory", None) or settings.get("default_territory") or get_root_of("Territory") or "All Territories"

        cust = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": p_doc.patient_name,
                "customer_type": "Individual",
                "customer_group": customer_group,
                "territory": territory,
            }
        ).insert(ignore_permissions=True, ignore_mandatory=True)
        cust_name = cust.name

    # If Patient has a customer field, link it for future use
    try:
        if frappe.get_meta("Patient").has_field("customer") and not frappe.db.get_value("Patient", p_doc.name, "customer"):
            frappe.db.set_value("Patient", p_doc.name, "customer", cust_name)
    except Exception:
        pass
    return cust_name


def _map_employee_to_practitioner(employee):
    # Kept for backward compatibility if needed; not used in current HMS flow
    return None


def update_validity_status():
    """Scheduled: update validity status daily"""
    validities = frappe.db.get_all("Fee Validity", {"status": ["not in", ["Expired", "Cancelled"]]})
    for v in validities:
        doc = frappe.get_doc("Fee Validity", v.name)
        doc.update_status()
        doc.save(ignore_permissions=True)
