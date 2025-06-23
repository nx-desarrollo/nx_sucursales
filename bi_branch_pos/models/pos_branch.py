# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import float_is_zero


class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.model_create_multi
    def create(self, vals):
        res = super(pos_session, self).create(vals)
        user_pool = self.env['res.users']
        branch_id = user_pool.browse(self.env.uid).branch_id.id or False
        if branch_id in res.config_id.pos_branch_ids.ids:
            res.branch_id = branch_id
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

    

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'


	pos_branch_ids = fields.Many2many(string='Branch', 
    related='pos_config_id.pos_branch_ids', readonly=False)


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def default_get(self,fields):
        res = super(pos_order, self).default_get(fields)
        if self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res
    
    @api.model
    def _payment_fields(self, order, ui_paymentline):
        values = super(pos_order, self)._payment_fields(order, ui_paymentline)
        values['branch_id'] = order.branch_id and order.branch_id.id or False
        return values

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines = self.env['pos.payment'].search(
            [('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[
                :1]
            if not cash_payment_method:
                raise UserError(
                    _("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'branch_id': order.branch_id.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_method_id': cash_payment_method.id,
            }
            order.add_payment(return_payment_vals)

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
