# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request

mapped = lambda b: {
    "id": b.id,
    "name": b.name,
    "company_id": b.company_id.id,
}

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session: dict = super().session_info()

        cids = [int(c) for c in request.httprequest.cookies.get("cids", "").strip().split("-") if bool(c)]
        companies = cids or self.env.companies.ids
        filtered = lambda b: b.company_id.id in companies
        user = self.env.user
         
        session["branch_id"] = user.branch_id.id if request.session.uid else None
        branches = user.branch_ids.filtered(filtered)

        if branches and user.branch_id.company_id.id not in companies:
            user.branch_id = branches[0]
        
        # Verificando si el usuario tiene asignado el permiso 'base.group_user':
        if user.has_group('base.group_user'):
            session.update({
                # Sucursales del usuario actualmente loggeado:
                "user_branches": {
                    'current_branch': user.branch_id.id,
                    'allowed_branches': branches.mapped(mapped),
                }
            })

        return session