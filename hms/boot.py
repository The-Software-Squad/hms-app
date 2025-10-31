import frappe

def boot_session(bootinfo):
    """Add HMS specific boot information to be sent to the frontend"""

    # HMS doctypes that should be exposed to frontend
    hms_doctypes = [
        "Patient",
        "Employee",
        "Patient Visit",
        "Lab Report",
        "Medicine",
        "Bed",
        "Ward",
        "Lab Report Type",
        "Healthcare Practitioner",
        "Practitioner Schedule",
        "Practitioner Schedule Time Slot",
        "Patient Appointment",
        "Fee Validity",
        "Fee Validity Reference"
    ]

    # Initialize dicts inside bootinfo
    bootinfo.hms_doctypes = {}
    bootinfo.hms_permissions = {}

    # Keep track of processed doctypes to avoid duplicates
    processed_doctypes = set()

    def process_doctype(doctype):
        """Helper function to process a single doctype"""
        if doctype in processed_doctypes:
            return
        processed_doctypes.add(doctype)

        try:
            # Get doctype metadata
            meta = frappe.get_meta(doctype)

            # Extract all fields for the doctype
            fields = []
            list_view_fields = []
            child_tables = []

            for field in meta.fields:
                # Skip non-data fields
                if field.fieldtype not in ['Section Break', 'Column Break', 'Tab Break', 'HTML']:
                    field_info = {
                        'fieldname': field.fieldname,
                        'fieldtype': field.fieldtype,
                        'label': field.label,
                        'options': field.options,
                        'reqd': field.reqd,
                        'in_list_view': field.in_list_view,
                        'read_only': field.read_only,
                        'hidden': field.hidden,
                        'default': field.default
                    }
                    fields.append(field_info)

                    # If this is a child table, add to child_tables to process later
                    if field.fieldtype == 'Table' and field.options not in processed_doctypes:
                        child_tables.append(field.options)

                    if field.in_list_view:
                        list_view_fields.append(field.fieldname)

            # Always include 'name' field in list view
            if 'name' not in list_view_fields:
                list_view_fields.insert(0, 'name')

            bootinfo.hms_doctypes[doctype] = {
                'fields': fields,
                'list_view_fields': list_view_fields,
                'title_field': meta.title_field or 'name',
                'search_fields': meta.search_fields,
                'sort_field': meta.sort_field or 'modified',
                'sort_order': meta.sort_order or 'DESC'
            }

            # Process any child tables
            for child_doctype in child_tables:
                process_doctype(child_doctype)

            # User permissions for this doctype
            if frappe.session.user != 'Guest':
                bootinfo.hms_permissions[doctype] = {
                    'read': frappe.has_permission(doctype, 'read'),
                    'create': frappe.has_permission(doctype, 'create'),
                    'write': frappe.has_permission(doctype, 'write'),
                    'delete': frappe.has_permission(doctype, 'delete')
                }

        except Exception as e:
            frappe.log_error(f"Error loading doctype {doctype}: {str(e)}", "HMS Boot Error")

    # Process all main doctypes
    for doctype in hms_doctypes:
        process_doctype(doctype)
