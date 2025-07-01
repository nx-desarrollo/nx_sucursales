from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals['branch_id'] = self.mapped('group_id.pos_order_id.session_id.branch_id').id
        return vals