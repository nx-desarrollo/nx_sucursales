# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ResBranch(models.Model):
	_inherit = "res.branch"

	analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica', readonly=True)
	allow_distribution = fields.Boolean(string='Permite distribución', default=False)

	@api.model_create_multi
	def create(self, vals_list):
		plan_id = self.env.ref('branch_analytic_account.branch_analytic_plan')
		for vals in vals_list:
			analytic_account_id = self.env['account.analytic.account'].create({
				'name': vals['name'],
				'plan_id': plan_id.id,
				'company_id': vals['company_id'],
			})
			vals['analytic_account_id'] = analytic_account_id.id
		return super(ResBranch, self).create(vals_list)

	def unlink(self):
		self.mapped('analytic_account_id').unlink()
		return super(ResBranch, self).unlink()