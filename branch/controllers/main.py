# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

# Controlador para establecer sucursal:
class SetBranch(http.Controller):
    @http.route('/set_branch', type='json', auth="public", website=True)
    def set_branch(self, branch_id):
        request.env.user.sudo().branch_id = branch_id