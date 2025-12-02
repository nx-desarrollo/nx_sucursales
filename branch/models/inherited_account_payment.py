# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    # En la V16 éste campo no está definido:
    branch_id = fields.Many2one(
        comodel_name='res.branch',
        string='Branch',
        default=lambda self: self.env.user.branch_id,
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)]
    )

    @api.depends('payment_type', 'branch_id')
    def _compute_available_journal_ids(self):
        """
        Get all journals having at least one payment method for inbound/outbound depending on the payment_type.
        """
        journals = self.env['account.journal'].search([('company_id', 'in', self.company_id.ids), ('type', 'in', ('bank', 'cash')), ('branch_ids', 'in', self.branch_id.ids), 
        ])
        journals_false = self.env['account.journal'].search([
            ('company_id', 'in', self.company_id.ids), ('type', 'in', ('bank', 'cash')), ('branch_ids', '=', False)
        ])
        journals += journals_false
        for pay in self:
            if pay.payment_type == 'inbound':
                pay.available_journal_ids = journals.filtered(
                    lambda j: j.company_id == pay.company_id and j.inbound_payment_method_line_ids.ids != []
                )
            else:
                pay.available_journal_ids = journals.filtered(
                    lambda j: j.company_id == pay.company_id and j.outbound_payment_method_line_ids.ids != []
                )

    def copy_data(self, default=None):
        
        data_list = super().copy_data(default)
        for payment, data in zip(self, data_list):
            if payment.branch_id:
                data['branch_id'] = payment.branch_id.id

        return data_list