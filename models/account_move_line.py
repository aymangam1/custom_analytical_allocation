# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    @api.model
    def create(self, vals):
        if 'move_id' in vals:
            move = self.env['account.move'].browse(vals['move_id'])
            if move.analytic_distribution and not vals.get('analytic_distribution'):
                vals['analytic_distribution'] = move.analytic_distribution
        return super().create(vals)

    @api.onchange('account_id','move_id')
    def _onchange_move_id_set_analytic_distribution(self):
        if self.move_id and self.move_id.analytic_distribution:
            self.analytic_distribution = self.move_id.analytic_distribution

    @api.ondelete(at_uninstall=False)
    def _unlink_except_posted(self):
        print("inside _unlink_except_posted")
        pass

