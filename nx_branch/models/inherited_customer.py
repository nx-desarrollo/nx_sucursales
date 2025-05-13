# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartnerIn(models.Model):
    _inherit = 'res.partner'

    
    @api.model_create_multi
    def default_get(self, default_fields):
        res = super(ResPartnerIn, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_ids' : self.env.user.branch_id.ids or False
            })
        return res

    branch_ids = fields.Many2many('res.branch', string="Branches")