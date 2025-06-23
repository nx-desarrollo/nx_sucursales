# -*- encoding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo import api

# Método post_init_hook para establecer a False el campo 'noupdate' a los registros de ir_model_data cuyo modelo sea 'ir.rule':
def post_init_hook(env):
    """
    website menu hide
    """
    env = api.Environment(env.cr, SUPERUSER_ID, {})
    env.cr.execute("""
                update ir_model_data set noupdate=False where
                model ='ir.rule' """)