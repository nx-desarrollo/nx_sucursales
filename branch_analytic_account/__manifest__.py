# -*- coding: utf-8 -*-
{
	'name': 'Nimetrix C.A. Branch analytic account',
	'version': '18.0',
	'category': 'Accounting/Accounting',
	'author': 'Nimetrix C.A.',
	'website': 'https://www.nimetrix.com',
	'summary': 'Branch analytic account',
	'description': '''
Branch analytic account
=======================
''',
	'depends': [
		'branch',
		'nimetrix_dual_currency',
	],
	'data': [
		'data/analytic_account_data.xml',
		'views/res_branch_view.xml',
		'views/analytic_line_views.xml',
		# 'views/bank_rec_widget_views.xml', # <--- No existe la vista 'account_accountant.view_bank_rec_widget_form' en la V18. Es más, no existen vistas para el modelo 'bank.rec.widget' en la V18.
	],
	'post_init_hook': '_branch_analytic_post_init',
	'application': False,
	'installable': True,
	'auto_install': False,
	'license': 'LGPL-3',
}