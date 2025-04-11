from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        payments = super().action_create_payments()

        payments = self.env['account.payment'].search(
            [('journal_id', '=', self.journal_id.id)], order="id desc", limit=1
        )
        print(f"payments: {payments}")

        if not payments:
            return payments

        invoice_ids = self._context.get('active_ids', [])
        print(f"Active invoice IDs: {invoice_ids}")

        for payment in payments:
            journal_entries = self.env['account.move.line'].search([
                ('move_id', '=', payment.move_id.id),
                ('account_id', '!=', False)
            ])
            print(f"journal_entries: {journal_entries}")

            original_entries = self.env['account.move.line'].search([
                ('move_id', 'in', invoice_ids),
                ('analytic_distribution', '!=', False)
            ])
            print(f"original_entries: {original_entries}")

            for line in journal_entries:
                print(f"journal_entries: {journal_entries}")
                for original in original_entries:
                    print(f"original_entries: {original_entries}")
                    # if line.account_id.id == original.account_id.id:
                    line.analytic_distribution = original.analytic_distribution
                    print(f"Updated line {line.id} with analytic_distribution: {original.analytic_distribution}")

        return payments
