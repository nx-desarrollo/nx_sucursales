# -*- coding: utf-8 -*-

from odoo import fields, models

class BankRecWidget(models.Model):
    _inherit = "bank.rec.widget"

    branch_id = fields.Many2one('res.branch', string='Sucursal', readonly=True)

    def _action_mount_line_in_edit(self, line_index, field_clicked=None):
        super(BankRecWidget, self)._action_mount_line_in_edit(line_index, field_clicked=field_clicked)
        self.branch_id = self.st_line_id.branch_id

    def _compute_analytic_distribution(self):
        super()._compute_analytic_distribution()
        for wizard in self:
            if wizard.form_account_id.account_type not in ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost'):
                continue
            analytic_distribution = wizard.analytic_distribution or {}
            if wizard.branch_id:
                analytic_distribution.update({str(wizard.branch_id.analytic_account_id.id): 100.0})
            wizard.analytic_distribution = analytic_distribution
            wizard._onchange_analytic_distribution()