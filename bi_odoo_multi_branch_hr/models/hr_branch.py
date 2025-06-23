# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command, _
from odoo.tools import pycompat
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    branch_id = fields.Many2one('res.branch', string='Branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    @api.model
    def default_get(self, flds):
        result = super(HrDepartment, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    branch_id = fields.Many2one('res.branch', string='Branch', domain=lambda self: [('id','in',[branch.id for branch in self.env.user.branch_ids])])

    @api.model
    def default_get(self, flds):
        result = super(HrApplicant, self).default_get(flds)
        user_obj = self.env['res.users']
        branch_id = user_obj.browse(self.env.user.id).branch_id.id
        result['branch_id'] = branch_id
        return result

    @api.onchange('job_id')
    def onchange_job_id(self):
        """ Override to get branch from department """

        department = self.env['hr.department'].browse(self.department_id.id)
        if department.branch_id:
            self.branch_id = department.branch_id

    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        dict_act_window = super(HrApplicant, self).create_employee_from_applicant()
        if dict_act_window.get('context'):
            dict_act_window.get('context').update({
                'default_branch_id': self.branch_id.id or False,
            })
        return dict_act_window


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.model
    def default_get(self, fields):
        rec = super(HrEmployee, self).default_get(fields)
        if self.env.user.branch_id.id:
            rec['branch_ids'] = self.env.user.branch_id.ids
        return rec


    # @api.onchange('branch_ids')
    # def _onchange_branch_ids(self):
    #     selected_brach = self.branch_ids
    #     if selected_brach:
    #         user_id = self.env['res.users'].browse(self.env.uid)
    #         user_branch = user_id.sudo().branch_ids
    #         if user_branch and selected_brach.ids in user_branch.ids :
    #             raise UserError(_("Please select active branch only."))

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    branch_ids = fields.Many2many('res.branch', compute="_compute_branches", string='Branches')

    @api.depends('employee_id')
    def _compute_branches(self):
        for rec in self:
            rec.branch_ids = rec.employee_id.branch_ids.ids

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.model
    def default_get(self, flds):
        """ Override to get default branch from employee """
        result = super(HrAttendance, self).default_get(flds)
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if employee_id:
            if employee_id.branch_ids:
                result['branch_ids'] = employee_id.branch_ids.ids
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_ids:
                self.update({'branch_ids': self.employee_id.branch_ids.ids})
            else:
                self.update({'branch_ids': False})


class HrContract(models.Model):
    _inherit = 'hr.contract'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.branch_id = self.employee_id.branch_ids.ids


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.model
    def default_get(self, flds):
        """ Override to get default branch from employee """
        result = super(HrPayslip, self).default_get(flds)
        employee_id = self.env['hr.employee'].browse(self._context.get('active_id'))
        result['branch_ids'] = employee_id.branch_ids.ids
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_ids:
                self.update({'branch_ids': self.employee_id.branch_ids.ids})
            else:
                self.update({'branch_ids': False})


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.model
    def default_get(self, flds):
        """ Override to get default branch from employee """
        result = super(HrExpenseSheet, self).default_get(flds)
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if employee_id:
            if employee_id.branch_ids:
                result['branch_ids'] = employee_id.branch_ids.ids
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_ids:
                self.update({'branch_ids': self.employee_id.branch_ids.ids})
            else:
                self.update({'branch_ids': False})


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    branch_ids = fields.Many2many('res.branch', string='Branches')

    @api.model
    def default_get(self, flds):
        """ Override to get default branch from employee """
        result = super(HrExpense, self).default_get(flds)

        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if employee_id:
            if employee_id.branch_ids:
                result['branch_ids'] = employee_id.branch_ids.ids
        return result

    @api.onchange('employee_id')
    def get_branch(self):
        if self.employee_id:
            if self.employee_id.branch_ids:
                self.update({'branch_ids': self.employee_id.branch_ids.ids})
            else:
                self.update({'branch_ids': False})

    def _get_default_expense_sheet_values(self):
        values = super(HrExpense, self)._get_default_expense_sheet_values()
        for val_ in range(len(values)):
            values[val_].update({
                'branch_ids': self.branch_ids.ids or False,
            })
        return values

    # def _prepare_move_values(self):
    #     """
    #     This function prepares move values related to an expense
    #     """
    #     self.ensure_one()
    #     journal = self.sheet_id.bank_journal_id if self.payment_mode == 'company_account' else self.sheet_id.journal_id
    #     account_date = self.sheet_id.accounting_date or self.date
    #     move_values = {
    #         'journal_id': journal.id,
    #         'company_id': self.sheet_id.company_id.id,
    #         'date': account_date,
    #         'ref': self.sheet_id.name,
    #         # force the name to the default value, to avoid an eventual 'default_name' in the context
    #         # to set it to '' which cause no number to be given to the account.move when posted.
    #         'name': '/',
    #         #'branch_ids': self.sheet_id.branch_ids.ids,
    #     }
    #     return move_values

    
    # def action_move_create(self):
    #     '''
    #     main function that is called when trying to create the accounting entries related to an expense
    #     '''
    #     moves = super(HrExpense, self).action_move_create()

    #     for sheet, move  in moves.items():
    #         move.write({
    #             'branch_id' : self.branch_id and self.branch_id.id or False
    #         })

    #     return moves