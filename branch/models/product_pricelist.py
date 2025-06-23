# -*- coding:utf-8 -*-

from odoo import api, models, fields, _

from odoo.exceptions import UserError

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def default_get(self, fields):
        rec = super(ProductPricelist, self).default_get(fields)
        if self.env.user.branch_ids.ids:
            rec['branch_ids'] = self.env.user.branch_id.ids
        return rec
    
    branch_ids = fields.Many2many('res.branch',string="Branches")

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     selected_brach = self.branch_id
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_id
    #         if user_branch and user_branch.id != selected_brach.id:
    #             raise UserError(_("Please select active branch only.")) 