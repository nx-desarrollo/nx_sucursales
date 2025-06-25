# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"
    
    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.stock_move_id and rec.stock_move_id.branch_id and not rec.branch_id:
                rec.branch_id = rec.stock_move_id.branch_id.id
            elif not rec.branch_id and self.env.user.branch_id:
                rec.branch_id = self.env.user.branch_id.id
        return res