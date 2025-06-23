# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Multi Branch for Account Budget(Enterprise Edition)",
    "version" : "18.0.0.1",
    "category" : "Accounting",
    'summary': 'Multi Branch budget management multiple branch budget multi branch multiple branch account budget multi unit operation for budget unit budget multiple branch budget operation unit for budget multiple analytic account multi branch analytic accounting branch',
    "description": """
       This odoo app works with enterprise editions and helps user to manage budget for multiple branch of single company, User can add branch on budget and select budgetary positions and analytic account with same branch and pass this to budget entries and analysis.
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.in",
    "price": 49,
    "currency": 'EUR',
    "depends" : ['branch','account_budget'],
    "data": [
        'security/budget_ir_rule.xml',
        'views/budget_view.xml',
        'views/account_analytic_account.xml',
        'views/account_analytic_line.xml',
        'views/account_move.xml',
        'views/budget_line_views.xml',
        'views/purchase_order.xml',
        # 'views/sale_order.xml', # El campo 'analytic_account_id' no existe en sale.order en la V18.
        # 'views/account_budget_post.xml', # <- Éste modelo no existe en la V18
        'views/account_move_line.xml',
    ],
    "license":'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/qCQxKJu4ikU',
    "images":["static/description/Banner.gif"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
