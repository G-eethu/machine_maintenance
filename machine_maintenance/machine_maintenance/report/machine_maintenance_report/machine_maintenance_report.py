# Copyright (c) 2025, Geethu and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    filters = filters or {}
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {"label": "Machine Name", "fieldname": "machine_name", "fieldtype": "Link", "options": "Item", "width": 180}
    ]

    if not filters.get("consolidated"):
        columns += [
            {"label": "Maintenance Date", "fieldname": "maintenance_date", "fieldtype": "Date", "width": 180},
            {"label": "Technician", "fieldname": "technician", "fieldtype": "Link","options": "Employee", "width": 180},
            {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 180},
        ]

    columns.append({"label": "Total Cost", "fieldname": "cost", "fieldtype": "Currency", "width": 180})
    return columns


def get_data(filters):
    conditions = []

    if filters.get("machine_name"):
        conditions.append(f"mm.machine_name = '{filters['machine_name']}'")

    if filters.get("technician"):
        conditions.append(f"mm.technician = '{filters['technician']}'")

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append(f"mm.maintenance_date BETWEEN '{filters['from_date']}' AND '{filters['to_date']}'")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    consolidated = filters.get("consolidated")

    if consolidated:
        query = f"""
            SELECT
                mm.machine_name,
                i.item_name AS machine_name,
                NULL AS maintenance_date,
                NULL AS technician,
                NULL AS status,
                SUM(mm.cost) AS cost
            FROM `tabMachine Maintenance` mm
            LEFT JOIN `tabItem` i ON i.name = mm.machine_name
            {where_clause}
            GROUP BY mm.machine_name, i.item_name
            ORDER BY mm.machine_name
        """

    else:
        query = f"""
            SELECT
                mm.machine_name,
                i.item_name AS machine_name,
                mm.maintenance_date,
                mm.technician,
                mm.status,
                mm.cost
            FROM `tabMachine Maintenance` mm
            LEFT JOIN `tabItem` i ON i.name = mm.machine_name
            {where_clause}
            ORDER BY mm.maintenance_date DESC
        """

    data = frappe.db.sql(query, as_dict=True)

    # --- Add color indicators for detailed view ---
    if not consolidated:
        for row in data:
            if row.status == "Overdue":
                row["indicator_color"] = "red"
            elif row.status == "Scheduled":
                row["indicator_color"] = "yellow"
            elif row.status == "Completed":
                row["indicator_color"] = "green"

    return data
