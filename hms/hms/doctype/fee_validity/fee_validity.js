// Copyright (c) 2025, HMS
// For license information, please see license.txt

frappe.ui.form.on('Fee Validity', {
  refresh(frm) {
    // Read-only document; created and maintained automatically
    if (!frm.is_new() && frm.doc.status === 'Active') {
      frm.add_custom_button(__('New Follow-up Visit'), () => make_follow_up_visit(frm), __('Create'));
    }
  },
});

function make_follow_up_visit(frm) {
  const route_options = {
    patient: frm.doc.patient,
    department: frm.doc.department,
    doctor: frm.doc.practitioner,
    visit_date: frappe.datetime.get_today(),
    fee_validity: frm.doc.name,
  };
  frappe.route_options = route_options;
  frappe.new_doc('Patient Visit');
}
