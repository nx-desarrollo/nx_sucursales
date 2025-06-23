# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def default_get(self, fields):
        rec = super(AccountJournal, self).default_get(fields)
        if self.env.user.branch_id:
            rec['branch_ids'] = [(6, 0, self.env.user.branch_id.ids)] if self.env.user.branch_id else False
        return rec

    branch_ids = fields.Many2many('res.branch', string="Branches")

    # @api.onchange('branch_ids')
    # def _onchange_branch_ids(self):
    #     selected_brach = self.branch_ids
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_ids
    #         if user_branch and selected_brach.ids in user_branch.ids :
    #             raise UserError(_("Please select active branch only."))
