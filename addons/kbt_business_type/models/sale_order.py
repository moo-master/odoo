from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Sale Order Type',
        required=True,
        domain="[('x_type', '=', 'sale'), ('active', '=', True)]",
    )

    @api.onchange('so_type_id')
    def _onchange_so_type_id(self):
        if not self.is_interface:
            self.name = self.so_type_id.x_sequence_id
