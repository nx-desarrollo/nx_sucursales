# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    branch_id = fields.Many2one(
        comodel_name='res.branch',
        string='Branch',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user.branch_id,
        domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)]
    )

    def _search_default_journal(self):
        if self.payment_ids and self.payment_ids[0].journal_id:
            return self.payment_ids[0].journal_id
        if self.statement_line_id and self.statement_line_id.journal_id:
            return self.statement_line_id.journal_id
        if self.statement_line_ids.statement_id.journal_id:
            return self.statement_line_ids.statement_id.journal_id[:1]

        journal_types = self._get_valid_journal_types()
        company_id = (self.company_id or self.env.company).id
        branch_id = (self.branch_id or self.env.user.branch_id).id
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types), ('branch_ids', 'in', [branch_id])]

        journal = None
        # the currency is not a hard dependence, it triggers via manual add_to_compute
        # avoid computing the currency before all it's dependences are set (like the journal...)
        if self.env.cache.contains(self, self._fields['currency_id']):
            currency_id = self.currency_id.id or self._context.get('default_currency_id')
            if currency_id and currency_id != self.company_id.currency_id.id:
                currency_domain = domain + [('currency_id', '=', currency_id)]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)
            branch = self.env['res.branch'].browse(branch_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s and branch %(branch_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                branch_name=branch.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal
    
    def write(self, vals):
        if 'branch_id' not in vals:
            for record in self.filtered(lambda r: not r.branch_id):
                if self.env.user.branch_id:
                    vals['branch_id'] = self.env.user.branch_id.id
                else:
                    raise UserError(_("The current user does not have an assigned branch. Please assign a branch to the user or provide a branch explicitly."))

        return super(AccountMove, self).write(vals)

    
    @api.depends('company_id', 'invoice_filter_type_domain', 'branch_id')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type), ('branch_ids', 'in', self.branch_id.ids)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.depends('move_type', 'branch_id')
    def _compute_journal_id(self):
        for record in self.filtered(lambda r: r.journal_id.type not in r._get_valid_journal_types() or r.branch_id not in r.journal_id.branch_ids):
            record.journal_id = record._search_default_journal()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    branch_id = fields.Many2one('res.branch', string='Branch', related='move_id.branch_id', store=True)