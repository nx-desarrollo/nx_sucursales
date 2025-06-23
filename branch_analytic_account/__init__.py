# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID

def _branch_analytic_post_init(env):
	env = api.Environment(env.cr, SUPERUSER_ID, {})
	
	plan_id = env.ref('branch_analytic_account.branch_analytic_plan')
	branch_ids = env['res.branch'].search([])

	for branch in branch_ids:
		branch_analytic_account_id = env['account.analytic.account'].create({
			'name': branch.name,
			'plan_id': plan_id.id,
			'company_id': branch.company_id.id,
		})
		branch.analytic_account_id = branch_analytic_account_id.id
		env.cr.execute('''
			UPDATE account_move_line aml
			SET analytic_distribution = COALESCE(analytic_distribution, '{}') || jsonb_build_object(%s::text, 100.0)
			FROM account_account aa
			WHERE
				aa.id = aml.account_id
				AND aml.company_id = %s
				AND aml.branch_id = %s
				AND aa.account_type IN ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost')
		''', [branch_analytic_account_id.id, branch.company_id.id, branch.id])
		
		env.cr.execute('''
			INSERT INTO account_analytic_line (name, date, journal_id, partner_id, unit_amount, product_id, product_uom_id, amount, nx_amount_ref, general_account_id, ref, move_line_id, company_id, currency_id, category, account_id, user_id, create_uid, write_uid, create_date, write_date)
			SELECT
				COALESCE(aml.name, aml.ref, '/'),
				aml.date,
				aml.journal_id,
				aml.partner_id,
				aml.quantity,
				aml.product_id,
				aml.product_uom_id,
				-aml.balance,
				-(aml.nx_debit_ref - aml.nx_credit_ref),
				aml.account_id,
				aml.ref,
				aml.id,
				aml.company_id,
				aml.company_currency_id,
				CASE
					WHEN am.move_type in ('out_invoice', 'out_refund') THEN 'invoice'
					WHEN am.move_type in ('in_invoice', 'in_refund') THEN 'vendor_bill'
					ELSE 'other'
				END,
				%s, %s, %s, %s,
				LOCALTIMESTAMP,
				LOCALTIMESTAMP
			FROM account_move_line aml
			JOIN account_move am ON am.id = aml.move_id
			JOIN account_account aa ON aa.id = aml.account_id
			WHERE am.state = 'posted' AND aml.company_id = %s AND aml.branch_id = %s AND aa.account_type IN ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost')
		''', [branch_analytic_account_id.id, SUPERUSER_ID, SUPERUSER_ID, SUPERUSER_ID, branch.company_id.id, branch.id])

		# El campo 'plan_id' no existe en la tabla 'account_analytic_line' en la V18
		# env.cr.execute('''
		# 	INSERT INTO account_analytic_line (name, date, journal_id, partner_id, unit_amount, product_id, product_uom_id, amount, amount_usd, general_account_id, ref, move_line_id, company_id, currency_id, category, plan_id, account_id, user_id, create_uid, write_uid, create_date, write_date)
		# 	SELECT
		# 		COALESCE(aml.name, aml.ref, '/'),
		# 		aml.date,
		# 		aml.journal_id,
		# 		aml.partner_id,
		# 		aml.quantity,
		# 		aml.product_id,
		# 		aml.product_uom_id,
		# 		-aml.balance,
		# 		-(aml.nx_debit_ref - aml.nx_credit_ref),
		# 		aml.account_id,
		# 		aml.ref,
		# 		aml.id,
		# 		aml.company_id,
		# 		aml.company_currency_id,
		# 		CASE
		# 			WHEN am.move_type in ('out_invoice', 'out_refund') THEN 'invoice'
		# 			WHEN am.move_type in ('in_invoice', 'in_refund') THEN 'vendor_bill'
		# 			ELSE 'other'
		# 		END,
		# 		%s, %s, %s, %s, %s,
		# 		LOCALTIMESTAMP,
		# 		LOCALTIMESTAMP
		# 	FROM account_move_line aml
		# 	JOIN account_move am ON am.id = aml.move_id
		# 	JOIN account_account aa ON aa.id = aml.account_id
		# 	WHERE am.state = 'posted' AND aml.company_id = %s AND aml.branch_id = %s AND aa.account_type IN ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost')
		# ''', [plan_id.id, branch_analytic_account_id.id, SUPERUSER_ID, SUPERUSER_ID, SUPERUSER_ID, branch.company_id.id, branch.id])