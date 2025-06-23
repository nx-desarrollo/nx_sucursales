# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MunicipalTaxes(models.Model):
    _inherit = 'municipal.taxes'

    @api.model
    def default_get(self, fields):
        rec = super(MunicipalTaxes, self).default_get(fields)
        if self.env.user.branch_id.id:
            rec['branch_id'] = self.env.user.branch_id.id
        return rec
    
    branch_id = fields.Many2one('res.branch', string="Branch", domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError(_("Please select active branch only."))