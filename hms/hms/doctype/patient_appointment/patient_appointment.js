// Copyright (c) 2025, HMS
// For license information, please see license.txt

frappe.ui.form.on('Patient Appointment', {
  start_time(frm) {
    // If end_time is empty, default to +30 minutes from start_time
    if (!frm.doc.start_time || frm.doc.end_time) return;
    try {
      const parts = (frm.doc.start_time || '').split(':').map(x => parseInt(x, 10));
      if (parts.length >= 2) {
        let h = parts[0];
        let m = parts[1] + 30;
        if (m >= 60) {
          h = (h + Math.floor(m / 60)) % 24;
          m = m % 60;
        }
        const hh = String(h).padStart(2, '0');
        const mm = String(m).padStart(2, '0');
        frm.set_value('end_time', `${hh}:${mm}:00`);
      }
    } catch (e) {
      // ignore
    }
  },
});

