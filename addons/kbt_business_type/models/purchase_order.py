from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )

    po_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Purchase Order Type',
        domain="[('x_type', '=', 'purchase'), ('is_active', '=', True)]",
    )
