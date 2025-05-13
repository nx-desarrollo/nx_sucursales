# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.model_create_multi
    def default_get(self,fields):
        res = super(SaleOrder, self).default_get(fields)
        branch_id = warehouse_id = False
        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',branch_id)])
            if branched_warehouse:
                warehouse_id = branched_warehouse.ids[0]
        
        if not warehouse_id:
            warehouse_id = self.env.user._get_default_warehouse_id()
            warehouse_id = warehouse_id.id

        res.update({
            'branch_id' : branch_id,
            'warehouse_id' : warehouse_id
        })

        return res

    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        self.change_branch_id()

    @api.constrains('branch_id')
    def constrains_branch_id(self):
        self.change_branch_id()

    @api.depends('branch_id')
    def change_branch_id(self):
        for line in self.order_line:
            line.branch_ids = False
            line.branch_ids += self.branch_id

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         branches = user_id.sudo().branch_ids.ids
    #         branches_user = [rec for rec in branches]
    #         if not(branches_user and selected_brach.id in branches_user):
    #             raise UserError(_("Please select active branch only."))

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_branch(self):
        return self._context['allowed_branch_ids']

    branch_ids = fields.Many2many('res.branch', string="Branch", default=_get_branch)
    
