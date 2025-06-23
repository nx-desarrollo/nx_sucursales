# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    branch_ids = fields.Many2many('res.branch', string="Allowed Branch")
    branch_id = fields.Many2one('res.branch', string= 'Branch')

    def write(self, values):
        if 'branch_id' in values or 'branch_ids' in values:
            self.env['ir.model.access'].call_cache_clearing_methods()
        user = super(ResUsers, self).write(values)
        return user

    @api.constrains('branch_id', 'branch_ids', 'active')
    def _check_branch(self):
        for user in self:
            if user.branch_id not in user.branch_ids:
                raise ValidationError(
                    _('Branch %(branch_name)s is not in the allowed branches for user %(user_name)s (%(branch_allowed)s).',
                    branch_name=user.branch_id.name,
                    user_name=user.name,
                    branch_allowed=', '.join(user.mapped('branch_ids.name')))
                )
    def _create_user_from_template(self, values):
        partner = self.env['res.partner'].browse([values['partner_id']])
        if partner.branch_ids:
            values.update({'branch_id': partner.branch_ids[0].id})
            values.update({'branch_ids': partner.branch_ids.ids})
        else:
            raise ValidationError(f'El contacto seleccionado ({partner.name}) no tiene configurada una sucursal para la creación del usuario.')
        res = super(ResUsers, self)._create_user_from_template(values)
        return res
    