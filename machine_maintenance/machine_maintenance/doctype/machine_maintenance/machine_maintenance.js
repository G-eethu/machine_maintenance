// Copyright (c) 2025, Geethu and contributors
// For license information, please see license.txt

frappe.ui.form.on("Machine Maintenance", {
    mark_completed(frm) {
        frappe.confirm(
            "Are you sure you want to mark this maintenance as completed?",
            () => {
                frm.set_value("status", "Completed");
                frm.set_value("completion_date", frappe.datetime.get_today());
                frm.save_or_update();
                frappe.show_alert({
                    message: __("Maintenance marked as Completed"),
                    indicator: "green",
                });
            }
        );
    },

    refresh(frm) {
        frm.toggle_display("notes_html", frm.doc.status !== "Scheduled");

        if (frm.doc.maintenance_date < frappe.datetime.get_today() && frm.doc.status !== "Completed") {
            frm.set_value("status", "Overdue");
        }
    },

    onload(frm) {
        if (frm.is_new()) {
            frm.set_value("maintenance_date", frappe.datetime.get_today());
        }
    },

    status(frm) {
        frm.toggle_display("notes_html", frm.doc.status !== "Scheduled");
    }
});


function show_notes(frm) {
    const crm_notes = new erpnext.utils.CRMNotes({
        frm: frm,
        notes_wrapper: $(frm.fields_dict.notes_html.wrapper),
    });
    crm_notes.refresh();
}

frappe.ui.form.on("Parts Used", {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        row.amount = row.qty * row.rate;
        frm.refresh_field("parts_used");
        calculate_total(frm);
    },
    rate(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        row.amount = row.qty * row.rate;
        frm.refresh_field("parts_used");
        calculate_total(frm);
    },
    parts_used_remove(frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let total = 0;
    frm.doc.parts_used.forEach((d) => {
        total += d.amount;
    });
    frm.set_value("cost", total);
}
