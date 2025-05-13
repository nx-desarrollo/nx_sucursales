# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.tools import SQL

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    branch_id = fields.Many2one('res.branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    def _select(self) -> SQL:
        return SQL("%s, move.branch_id as  branch_id", super()._select())
    