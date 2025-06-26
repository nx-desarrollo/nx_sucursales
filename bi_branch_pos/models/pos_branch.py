# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import float_is_zero

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     @api.model_create_multi
#     def create(self, vals_list):
#         res = super().create(vals_list)
#         for rec in res:
#             if not rec.pos_order_ids:
#                 if rec.stock_move_id and rec.stock_move_id.branch_id:
#                     rec.branch_id = rec.stock_move_id.branch_id
#                 elif self.env.user.branch_id:
#                     rec.branch_id = self.env.user.branch_id
#                 else:
#                     raise UserError(_("No se pudo asignar una sucursal. Asegúrese de que el movimiento o el usuario tengan una sucursal configurada."))
#         raise UserError(f'res: {res}')
#         return res
        
class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.model_create_multi
    def create(self, vals):
        res = super(pos_session, self).create(vals)
        # user_pool = self.env['res.users']
        # branch_id = user_pool.browse(self.env.uid).branch_id.id or False
        # if branch_id in res.config_id.pos_branch_ids.ids:
        #     res.branch_id = branch_id
        for rec in res:
            branch_id = self.env.user.branch_id if self.env.user.branch_id else False
            if res.config_id.pos_branch_ids:
                branch_id = res.config_id.pos_branch_ids[0]
            rec.branch_id = branch_id.id if branch_id else False
        return res

    def _loader_params_pos_session(self):
        res = super(pos_session, self)._loader_params_pos_session()
        fields = res.get('search_params').get('fields')
        fields.extend(['branch_id'])
        res['search_params']['fields'] = fields
        return res

    branch_id = fields.Many2one('res.branch', 'Branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

class pos_config(models.Model):
    _inherit = 'pos.config'

    pos_branch_ids = fields.Many2many(
        'res.branch', 'user_id', 'branch_id', string='Branch')

    @api.model
    def get_pos_branch_ids(self, config_ids):
        pos_configs = self.browse(config_ids)
        if pos_configs:
            return [{'id': b.id, 'name': b.name} for b in pos_configs.pos_branch_ids]
        return []

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'


	pos_branch_ids = fields.Many2many(string='Branch', 
    related='pos_config_id.pos_branch_ids', readonly=False)


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            # raise UserError(f'rec.session_id.branch_id: {rec.session_id.branch_id}')
            rec.branch_id = rec.session_id.branch_id.id if rec.session_id and rec.session_id.branch_id else False
        return res

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        values = super(pos_order, self)._payment_fields(order, ui_paymentline)
        values['branch_id'] = order.branch_id and order.branch_id.id or False
        return values

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        vals['branch_id'] = self.session_id.branch_id.id if self.session_id and self.session_id.branch_id else False
        return vals

    # OVERRIDE: Sucursales
    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.

        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.currency_id.decimal_places

        # Recompute amount paid because we don't trust the client
        order.with_context(backend_recomputation=True).write({'amount_paid': sum(order.payment_ids.mapped('amount'))})

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No se encontró ningún extracto de caja para esta sesión. No se pudo registrar el efectivo devuelto."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Datetime.now(),
                'payment_method_id': cash_payment_method.id,
                'is_change': True,
                # UPDATE: Sucursal:
                'branch_id': order.branch_id.id if order.branch_id else False,
            }
            order.add_payment(return_payment_vals)
            order._compute_prices()

    def _prepare_invoice_vals(self):
        values = super(pos_order, self)._prepare_invoice_vals()
        values['branch_id'] = self.branch_id and self.branch_id.id or False
        return values

    def _prepare_invoice_line(self, order_line):
        values = super(pos_order, self)._prepare_invoice_line(order_line)
        values['branch_id'] = self.branch_id and self.branch_id.id or False
        return values

    def _prepare_procurement_group_vals(self):
        values = super(pos_order, self)._prepare_procurement_group_vals()
        values['branch_id'] = self.branch_id and self.branch_id.id or False
        return values

    def _prepare_procurement_values(self, group_id=False):
        values = super(pos_order, self)._prepare_procurement_values()
        values['branch_id'] = self.branch_id and self.branch_id.id or False
        return values

    # @api.model_create_multi
    # def create(self, vals):
    #     res = super(pos_order, self).create(vals)
    #     res.branch_id = res.session_id.branch_id.id
    #     return res

    branch_id = fields.Many2one('res.branch', 'Branch')

    @api.constrains('state')
    def constrains_branch_id(self):
        for item in self:
            item.get_branch_id()

    @api.onchange('state')
    def onchange_branch_id(self):
        for item in self:
            item.get_branch_id()

    def get_branch_id(self):
        for picking in self.picking_ids:
            picking.branch_id = self.branch_id.id

class PosPaymentIn(models.Model):
    _inherit = "pos.payment"

    branch_id = fields.Many2one('res.branch', 'Branch')

class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    branch_ids = fields.Many2many('res.branch', string='Branches')

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError(_("Please select active branch only."))
