// Copyright (c) 2025, Geethu and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Maintenance Report"] = {
    "filters": [
        {
            fieldname: "machine_name",
            label: __("Machine"),
            fieldtype: "Link",
            options: "Item"
        },
        {
            fieldname: "technician",
            label: __("Technician"),
            fieldtype: "Link",
			options: "Employee"
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "consolidated",
            label: __("Consolidated"),
            fieldtype: "Check",
            default: 0
        }
    ]
};