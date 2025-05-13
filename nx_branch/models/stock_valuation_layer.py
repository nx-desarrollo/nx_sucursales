# -*- coding:utf-8 -*-

from odoo import api, models, fields

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model
    def default_get(self, fields):
        rec = super(StockValuationLayer, self).default_get(fields)
        if self.env.user.branch_id.id:
            rec['branch_id'] = self.env.user.branch_id.id
        return rec
    
    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])