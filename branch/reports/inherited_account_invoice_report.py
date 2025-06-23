# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools import SQL

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    branch_id = fields.Many2one('res.branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    @api.model
    def _where(self) -> SQL:
        where_clause = '''
            WHERE move.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
              AND line.account_id IS NOT NULL
              AND line.display_type = 'product'
        '''
        
        branch_id = self._context.get('branch_id')
        if branch_id:
            where_clause += f'\n  AND move.branch_id = {int(branch_id)}'

        return SQL(where_clause)