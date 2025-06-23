# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountAnalyticLine(models.Model):
	_inherit = "account.analytic.line"

	# 'amount_usd' fue cambiado por 'nx_amount_ref':
	# amount_usd = fields.Monetary(string='Importe $', default=0.0, currency_field='nx_currency_ref_id')
	nx_amount_ref = fields.Monetary(string='Importe Ref', default=0.0, currency_field='nx_currency_ref_id')
	nx_currency_ref_id = fields.Many2one(related='company_id.nx_currency_ref_id', string='Moneda Dual Ref.')