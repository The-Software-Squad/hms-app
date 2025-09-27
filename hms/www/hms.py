import json
import re
import frappe
from frappe import _

# Regex patterns to strip <script> tags (XSS prevention)
SCRIPT_TAG_PATTERN = re.compile(r"\<script[^<]*\</script\>")
CLOSING_SCRIPT_TAG_PATTERN = re.compile(r"</script\>")


def get_context(context):
    """Get context for HMS frontend page"""

    # CSRF token (same approach as Raven)
    csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()  # ensure CSRF token is saved

    # Boot data: guest vs logged-in user
    if frappe.session.user == "Guest":
        from frappe.website.utils import get_boot_data
        bootinfo = get_boot_data()
    else:
        bootinfo = frappe.sessions.get()

    # Apply boot_session hooks (extend bootinfo)
    for boot_function_path in frappe.get_hooks("boot_session"):
        boot_function = frappe.get_attr(boot_function_path)
        boot_function(bootinfo)

    # Convert to JSON and sanitize
    boot_json = frappe.as_json(bootinfo, indent=None, separators=(",", ":"))
    boot_json = SCRIPT_TAG_PATTERN.sub("", boot_json)
    boot_json = CLOSING_SCRIPT_TAG_PATTERN.sub("", boot_json)

    # Double encode JSON string (safer to embed inline)
    boot_json = json.dumps(boot_json)

    # Put into context
    context.boot = boot_json
    context.app_name = "HMS"
    context.csrf_token = csrf_token

    return context
