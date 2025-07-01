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
            branch_id = self.env.user.branch_id
        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', branch_id.id)])
            if branched_warehouse:
                warehouse_id = branched_warehouse.ids[0]
        
        # if not warehouse_id and branch_id:
            # raise UserError(f'No se encontró un almacén para la sucursal {branch_id.name}.')
            # warehouse_id = self.env.user._get_default_warehouse_id()
            # warehouse_id = warehouse_id.id

        res.update({
            'branch_id' : branch_id.id if branch_id else False,
            'warehouse_id' : warehouse_id
        })

        return res

    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    @api.depends('user_id', 'company_id', 'branch_id')
    def _compute_warehouse_id(self):
        for order in self:
            # =================== Inicio de método nativo =================== #
            default_warehouse_id = self.env['ir.default'].with_company(
                order.company_id.id)._get_model_defaults('sale.order').get('warehouse_id')
            if order.state in ['draft', 'sent'] or not order.ids:
                # Should expect empty
                if default_warehouse_id is not None:
                    order.warehouse_id = default_warehouse_id
                else:
                    order.warehouse_id = order.user_id.with_company(order.company_id.id)._get_default_warehouse_id()
            # =================== Fin de método nativo =================== #

            # =================== Inicio de método aplicando sucursales =================== #
            if order.branch_id:
                branched_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', order.branch_id.id)])
                if branched_warehouse:
                    order.warehouse_id = branched_warehouse.ids[0]
                else:
                    order.warehouse_id = False
            # =================== Fin de método aplicando sucursales =================== #

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for order in res:
            order._validate_branch_vs_warehouse()
        return res

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            order._validate_branch_vs_warehouse()
            if order.order_line and order.branch_id: 
                for line in order.order_line:
                    line.branch_id = order.branch_id.id
        return res

    def _validate_branch_vs_warehouse(self):
        """
        Asegura que el almacén (warehouse_id) pertenezca a la misma sucursal (branch_id).
        """
        for order in self:
            branch_id = order.branch_id
            warehouse_id = order.warehouse_id
            warehouse_branch = warehouse_id.branch_id if warehouse_id else False

            if not warehouse_id and branch_id:
                raise UserError(f'Por favor, establezca un almacén para la sucursal {branch_id.name}.')

            if branch_id and warehouse_id and warehouse_branch:
                if branch_id.id != warehouse_branch.id:
                    raise UserError(_(
                        'El almacén "%s" no pertenece a la sucursal "%s".'
                    ) % (warehouse_id.display_name, branch_id.name))

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    branch_id = fields.Many2one('res.branch', string="Branch")    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'order_id' in vals and 'branch_id' not in vals:
                order = self.env['sale.order'].browse(vals['order_id'])
                if order.branch_id:
                    vals['branch_id'] = order.branch_id.id
        return super().create(vals_list)    