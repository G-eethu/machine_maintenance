// Copyright (c) 2025, Geethu and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machine Maintenance", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) return;
        show_notes(frm);
    },
});

function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();
}

