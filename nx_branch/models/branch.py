# -*- coding: utf-8 -*-

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True)
    telephone = fields.Char(string='Telephone No')
    address = fields.Text('Address')
    main_branch = fields.Boolean('Sucursal principal', default=False)
    # sequence = fields.Integer(default=10)

    @api.constrains('main_branch', 'company_id')
    def _constrains_main_branch(self):
        for branch in self:
            if branch.main_branch and self.search([('main_branch', '=', True), ('company_id', '=', branch.company_id.id), ('id', '!=', branch.id)], limit=1):
                raise ValidationError('Ya existe una sucursal marcada como principal para esta compañía.')

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain =  []

        if self._context.get('allowed_company_ids'):
            selected_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
            if selected_company_ids:
                branches_ids = self.env['res.branch'].search([('company_id','in',selected_company_ids.ids)])
                args += [('id', 'in', branches_ids.ids)]
                return super(ResBranch, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                name_get_uid=name_get_uid)
            return super(ResBranch, self)._name_search(name=name, args=args, operator=operator, limit=limit,name_get_uid=name_get_uid)