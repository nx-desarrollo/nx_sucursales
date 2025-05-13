# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """ Add information about iap enrich to perform """
        session_info = super(Http, self).session_info()

        user = self.env.user
        if user.has_group('base.group_user'):
            session_info.update({
                'user_branches': {
                    'current_branch': user.branch_id.id,
                    'allowed_branches': {
                        branch.id: {
                            'id': branch.id,
                            'name': branch.name,
                            'company': branch.company_id.id,
                        } for branch in user.branch_ids
                    },
                },
                'display_switch_branch_menu': user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
                'allowed_branch_ids' : user.branch_id.ids
            })
        return session_info