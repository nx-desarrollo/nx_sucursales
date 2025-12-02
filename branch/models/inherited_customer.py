# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartnerIn(models.Model):
    _inherit = 'res.partner'

    
    #Función comentada para evitar que se asigne la sucursal del usuario al crear un contacto
    # @api.model_create_multi
    # def default_get(self, default_fields):
    #     res = super(ResPartnerIn, self).default_get(default_fields)
    #     if self.env.user.branch_id:
    #         res.update({
    #             'branch_ids': [(6, 0, self.env.user.branch_id.ids)] if self.env.user.branch_id else False # Cambio a formato de lista para adecuarlo al estandar de Odoo
    #         })
    #     return res

    branch_ids = fields.Many2many('res.branch', string="Branches")