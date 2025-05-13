# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request

class SetBranch(http.Controller):

    @http.route('/set_brnach', type='json', auth="public", methods=['POST'], website=True)
    def custom_hours(self, user, branch, **post):
        user_id = request.env['res.users'].sudo().search([('id', '=', user)])
        user_id.branch_id = branch
        return