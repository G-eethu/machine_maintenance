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
        self.send_maintenance_notification()

    def validate(self):
        self.send_maintenance_notification()


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
        je.custom_machine_maintenance = self.name
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


    def send_maintenance_notification(self):
        """Send notifications based on current status"""
        subject = ""
        message = ""
        recipients = []
        technician_email = None
        if self.technician:
            technician_email = frappe.db.get_value("Employee", self.technician, "user_id")

        company_email = frappe.db.get_single_value("Maintenance Settings", "default_notification_email") \
            if frappe.db.exists("DocType", "Maintenance Settings") else None

        if technician_email:
            recipients.append(technician_email)
        elif company_email:
            recipients.append(company_email)

        if not recipients:
            frappe.logger().info(f"No email recipients found for Machine Maintenance {self.name}")
            return

        if self.status == "Completed":
            subject = f"Maintenance Completed for {self.machine_name}"
            message = f"""
                <p>Hello,</p>
                <p>The maintenance for <b>{self.machine_name}</b> has been marked as <b>Completed</b>.</p>
                <p>Date: {self.maintenance_date}</p>
                <p>Technician: {self.technician or 'N/A'}</p>
                <p>Total Cost: {self.cost or 0}</p>
            """

        elif self.status == "Scheduled":
            subject = f"Maintenance Scheduled for {self.machine_name}"
            message = f"""
                <p>Hello,</p>
                <p>The maintenance for <b>{self.machine_name}</b> is <b>Scheduled</b> on {self.maintenance_date}.</p>
                <p>Assigned Technician: {self.technician or 'N/A'}</p>
            """

        elif self.status == "Overdue":
            subject = f"Maintenance Overdue for {self.machine_name}"
            message = f"""
                <p>Hello,</p>
                <p>The maintenance for <b>{self.machine_name}</b> is <b>Overdue</b> since {self.maintenance_date}.</p>
                <p>Please take immediate action.</p>
            """

        if subject and message:
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message,
                reference_doctype=self.doctype,
                reference_name=self.name
            )
            frappe.msgprint(f" Email sent for status <b>{self.status}</b>.")

