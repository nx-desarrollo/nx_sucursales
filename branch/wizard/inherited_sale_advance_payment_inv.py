# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'


    def _create_invoice(self, order, so_line, amount):
        result = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)

        branch_id = False

        if order.branch_id:
            branch_id = order.branch_id.id
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id

        result.write({
            'branch_id' : branch_id
            })

        return result

class AccountPaymentRegisterInv(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields):
        rec = super(AccountPaymentRegisterInv, self).default_get(fields)
        move_id = self.env['account.move'].browse(self._context.get('move_id', False))
        if move_id:
            rec['branch_id'] = move_id.branch_id.id if move_id and move_id.branch_id else False 
        else:
            invoice_defaults = self.env['account.move'].browse(self._context.get('active_ids', []))
            if invoice_defaults and len(invoice_defaults) == 1:
                rec['branch_id'] = invoice_defaults.branch_id.id
        return rec

    branch_id = fields.Many2one('res.branch')

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals['branch_id'] = self.branch_id.id if self.branch_id else False
        return payment_vals

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError(_("Please select active branch only."))