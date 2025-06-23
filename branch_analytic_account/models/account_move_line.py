# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import float_compare

class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	def _set_branch_analytic_account(self):
		branch_analytic_ids = self.env['res.branch'].search([]).mapped('analytic_account_id').ids
		from_onchange = self._context.get('from_onchange')
		for line in self:
			if line.account_type not in ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost'):
				continue

			analytic_distribution = line.analytic_distribution or {}
			if line.branch_id:
				if not line.branch_id.allow_distribution or (not from_onchange and line._origin and line._origin.branch_id != line.branch_id):
					analytic_distribution = {k: v for k, v in analytic_distribution.items() if int(k) not in branch_analytic_ids}
				analytic_distribution.update({str(line.branch_id.analytic_account_id.id): 100.0})
			line.analytic_distribution = analytic_distribution

	@api.model_create_multi
	def create(self, vals_list):
		lines = super(AccountMoveLine, self).create(vals_list)
		lines._set_branch_analytic_account()
		return lines

	@api.onchange('analytic_distribution')
	def _inverse_analytic_distribution(self):
		self.with_context(from_onchange=True)._set_branch_analytic_account()
		super(AccountMoveLine, self)._inverse_analytic_distribution()

	def _prepare_analytic_distribution_line(self, distribution, account_id, distribution_on_each_plan):
		res = super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution, account_id, distribution_on_each_plan)
		account = self.env['account.analytic.account'].browse(int(account_id))
		distribution_plan = distribution_on_each_plan.get(account.root_plan_id, 0) + distribution
		decimal_precision = self.env['decimal.precision'].precision_get('Percentage Analytic')
		if float_compare(distribution_plan, 100, precision_digits=decimal_precision) == 0:
			amount = -(self.nx_debit_ref - self.nx_credit_ref) * (100 - distribution_on_each_plan.get(account.root_plan_id, 0)) / 100.0
		else:
			amount = -(self.nx_debit_ref - self.nx_credit_ref) * distribution / 100.0
		res['nx_amount_ref'] = amount
		return res


class AccountMove(models.Model):
	_inherit = "account.move"

	@api.onchange('branch_id')
	def _onchange_analytic_branch_id(self):
		self.line_ids._set_branch_analytic_account()