# -*- coding: utf-8 -*-

from odoo import fields, models, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env.user.branch_id, domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)])
    
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('branch_id') and val.get('origin'):
                branch_sale_order = self.env['sale.order'].search([('name', '=', val.get('origin')), ('company_id', '=', val.get('company_id'))], limit=1).branch_id
                if branch_sale_order:
                    val['branch_id'] = branch_sale_order.id
        return super().create(vals_list)
        