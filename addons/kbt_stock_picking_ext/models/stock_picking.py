from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean('Interface')
