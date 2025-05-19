# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multiple Branch Unit Operation Setup for All Applications Odoo',
    'version': '18.0.0.1',
    'category': 'branch',
    'summary': 'Multiple Branch Management Multi Branch app Multiple Unit multiple Operating unit sales branch Sales Purchase branch Invoicing branch billing Voucher branch warehouse branch Payment branch Accounting Reports for single company Multi Branches multi company',
    "description": """
       
       """,
    'author': 'Nimetrix',
    'website': 'https://nimetrix.com',
    'depends': ['base', 'sale_management', 'purchase', 'stock', 'account', 'purchase_stock','web','stock_account',],
    # 'uninstall_hook': '_uninstall_hook',
    'data': [
        'security/branch_security.xml',
        'security/multi_branch.xml',
        'security/ir.model.access.csv',
        'views/res_branch_view.xml',
        'views/inherited_res_users.xml',
        'views/inherited_sale_order.xml',
        'views/inherited_stock_picking.xml',
        'views/inherited_stock_move.xml',
        'views/inherited_account_invoice.xml',
        'views/inherited_purchase_order.xml',
        'views/inherited_stock_warehouse.xml',
        'views/inherited_account_bank_statement.xml',
        'wizard/inherited_account_payment.xml',
        'views/inherited_product.xml',
        'views/inherited_partner.xml',
        'views/account_journal_views.xml',
        'views/product_pricelist_views.xml',
        'views/stock_valuation_layer.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'nx_branch/static/src/js/session.js',
            # 'nx_branch/static/src/js/branch_service.js',
            'nx_branch/static/src/xml/branch.xml'
        ]
    },
    'license' : 'OPL-1',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.gif'],
    # 'post_init_hook': 'post_init_hook',
}

