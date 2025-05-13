# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    branch_id = fields.Many2one('res.branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['branch_id'] = "s.branch_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.branch_id"""
        return res