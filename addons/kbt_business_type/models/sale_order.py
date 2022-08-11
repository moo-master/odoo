from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )

    so_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Sale Order Type',
        domain="[('x_type', '=', 'sale'), ('is_active', '=', True)]",
    )
