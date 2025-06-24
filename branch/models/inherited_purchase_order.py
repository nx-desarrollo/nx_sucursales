# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.exceptions import UserError


class purchase_order(models.Model):

    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        result = super(purchase_order, self)._prepare_account_move_line(move)
        result.update({
            'branch_id': self.order_id.branch_id.id or False,

        })
        return result

    @api.model
    def default_get(self, default_fields):
        res = super(purchase_order, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({'branch_id': branch_id})
        return res

    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    def _prepare_stock_moves(self, picking):
        result = super(purchase_order, self)._prepare_stock_moves(picking)

        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        for res in result:
            res.update({'branch_id': branch_id})

        return result


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrder, self).default_get(fields)
        branch_id = picking_type_id = False

        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', branch_id)])
            if branched_warehouse:
                picking_type_id = branched_warehouse[0].in_type_id.id
        
        if not picking_type_id:
            picking_type = self._default_picking_type()
            picking_type_id = picking_type.id if picking_type and picking_type.branch_id and picking_type.branch_id and picking_type.branch_id.id in self.env.user.branch_ids.ids else False

        # raise UserError(f'picking_type_id: {picking_type_id}')
        res.update({
            'branch_id': branch_id,
            'picking_type_id': picking_type_id
        })

        return res

    branch_id = fields.Many2one('res.branch', string='Sucursal', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    # Vaciar campo 'picking_type_id' al cambiar el valor de 'branch_id':
    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     for rec in self:
    #         rec.picking_type_id = False

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for order in res:
            if order.origin:
                sale = self.env['sale.order'].search([('name', '=', order.origin)], limit=1)
                if sale:
                    order.branch_id = sale.branch_id.id

            order._validate_branch_vs_picking()
        return res

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if vals.get('origin'):
                sale = self.env['sale.order'].search([('name', '=', vals['origin'])], limit=1)
                if sale:
                    order.branch_id = sale.branch_id.id

            order._validate_branch_vs_picking()
        return res

    def _validate_branch_vs_picking(self):
        """
        Verifica que picking_type_id pertenezca a la misma sucursal que el pedido.
        """
        for order in self:
            branch = order.branch_id
            picking_type = order.picking_type_id

            # Obtener sucursal del picking_type
            picking_branch = picking_type.warehouse_id.branch_id if picking_type and picking_type.warehouse_id else False

            if branch and picking_type and picking_branch:
                if branch.id != picking_branch.id:
                    raise UserError(_(
                        'El tipo de operación "%s" no pertenece a la sucursal "%s".'
                    ) % (picking_type.name, branch.name))

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id': branch_id
        })
        return res

    def _prepare_invoice(self):
        result = super(PurchaseOrder, self)._prepare_invoice()
        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        result.update({

            'branch_id': branch_id
        })

        return result

    def action_view_invoice(self, invoices=False):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''

        result = super(PurchaseOrder, self).action_view_invoice(invoices)

        branch_id = False
        if self.branch_id:
            branch_id = self.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        result.update({
            'branch_id': branch_id
        })

        return result

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError(_("Please select active branch only."))

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    pickings = picking
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                # Get following pickings (created by push rules) to confirm them as well.
                forward_pickings = self.env['stock.picking']._get_impacted_pickings(moves)
                if self.branch_id:
                    for record in forward_pickings:
                        record.branch_id = self.branch_id.id
                (pickings | forward_pickings).action_confirm()
                # El método 'message_post_with_view' no existe en la V18:
                # picking.message_post_with_view('mail.message_origin_link',
                #     values={'self': picking, 'origin': order},
                #     subtype_id=self.env.ref('mail.mt_note').id)
        return True