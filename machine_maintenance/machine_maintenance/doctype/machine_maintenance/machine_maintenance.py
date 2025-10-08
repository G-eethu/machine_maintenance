# Copyright (c) 2025, Geethu and contributors
# For license information, please see license.txt

import frappe
from erpnext.crm.utils import CRMNote
from frappe.utils import flt


class MachineMaintenance(CRMNote):

    def on_submit(self):
        if not self.technician:
            frappe.throw("Technician must be assigned before submission.")
        self.create_journal_entry()


    def create_journal_entry(self):
        """Create Journal Entry dynamically using Company custom accounts"""
        company = frappe.defaults.get_user_default("Company")

        maintenance_expense_account = frappe.db.get_value("Company", company, "custom_maintenance_expense_account")
        cash_bank_account = (
            frappe.db.get_value("Company", company, "default_cash_account")
            or frappe.db.get_value("Company", company, "default_bank_account")
        )

        if not maintenance_expense_account:
            frappe.throw(f"Please set the 'Maintenance Expense Account' in the Company master .")
        if not cash_bank_account:
            frappe.throw(f"Please set a Default Cash or Bank Account in the Company master.")

        cost = flt(self.cost)

        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = company
        je.posting_date = self.maintenance_date
        je.remark = f"Maintenance cost for {self.machine_name} ({self.name})"

        je.append("accounts", {
            "account": maintenance_expense_account,
            "debit_in_account_currency": cost,
            "exchange_rate": 1
        })

        je.append("accounts", {
            "account": cash_bank_account,
            "credit_in_account_currency": cost,
            "exchange_rate": 1
        })

        je.save(ignore_permissions=True)
        je.submit()

        frappe.msgprint(f"Journal Entry <b>{je.name}</b> created for maintenance cost.")
