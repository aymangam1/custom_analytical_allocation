from odoo import api, fields, models, _
from datetime import date, datetime, time
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    analytic_distribution = fields.Json(string="Analytic", store=True, readonly=False,)
    analytic_precision = fields.Integer(default=lambda self: self.env["decimal.precision"].precision_get("Percentage Analytic"))

    @api.onchange('move_id')
    def set_analytic_distribution(self):
        if self.move_id and self.move_id.analytic_distribution:
            self.analytic_distribution = self.move_id.analytic_distribution



    def _get_unbalanced_moves(self, container):
        moves = container['records'].filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend on computed stored fields.
        # It happens as the ORM calls create() with the 'no_recompute' statement.
        self.env['account.move.line'].flush_model(['debit', 'credit', 'balance', 'currency_id', 'move_id'])
        self._cr.execute('''
            SELECT line.move_id,
                   ROUND(SUM(line.debit), currency.decimal_places) debit,
                   ROUND(SUM(line.credit), currency.decimal_places) credit
              FROM account_move_line line
              JOIN account_move move ON move.id = line.move_id
              JOIN res_company company ON company.id = move.company_id
              JOIN res_currency currency ON currency.id = company.currency_id
             WHERE line.move_id IN %s
          GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.balance), currency.decimal_places) = 0
        ''', [tuple(moves.ids)])


    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.split_payable_line()
        return record

    #

    # def write(self, vals):
    #     res = super().write(vals)
    #     self._split_payable_line()
    #     return res


    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_split_line') and any(
                field in vals for field in
                ('invoice_line_ids', 'line_ids', 'partner_id', 'currency_id', 'invoice_date_due')
        ):
            for move in self:
                move.with_context(skip_split_line=True).split_payable_line()
        return res

    def split_payable_line(self):
        for move in self:
            if move.move_type != 'in_invoice':
                continue

            payable_lines = self.env['account.move.line'].search([
                ('move_id', '=', move.id),
                ('account_internal_group', '=', 'liability'),
                ('display_type', '=', 'payment_term')
            ])

            invoice_lines = self.env['account.move.line'].search([
                ('move_id', '=', move.id),
                ('account_internal_group', '!=', 'liability'),
            ])

            if not invoice_lines:
                continue
            payable_lines.with_context(dynamic_unlink=True).unlink()

            for line in invoice_lines:
                amount = -line.balance

                if amount:
                    date_maturity = move.invoice_date_due or date.today()
                    print(f" =====> {self.partner_id.property_account_payable_id.id}")

                    self.env['account.move.line'].create({
                        'move_id': move.id,
                        'account_id': self.partner_id.property_account_payable_id.id,
                        'partner_id': move.partner_id.id,
                        'name': line.name or move.name or '/',
                        'date_maturity': date_maturity,
                        'debit': amount if amount > 0 else 0.0,
                        'credit': -amount if amount < 0 else 0.0,
                        'amount_currency': -line.amount_currency if line.amount_currency else 0,
                        'balance': amount,
                        'currency_id': move.currency_id.id,
                        'analytic_distribution': line.analytic_distribution,
                        'display_type': 'payment_term',
                    })

    def action_post(self):
        res = super().action_post()
        if self.move_type == 'in_invoice':
            self.split_payable_line()
        return res

    @api.model
    def process_all_vendor_bills(self):
        """تطبيق دالة split_payable_line على جميع فواتير الموردين الموجودة"""
        # vendor_bills = self.env['account.move'].search([('move_type', '=', 'in_invoice')])
        vendor_bills = self.env['account.move'].search([])

        for bill in vendor_bills:
            bill.split_payable_line()
            print(f"تم تطبيق دالة split_payable_line على الفاتورة: {bill.name}")




