from odoo import models, fields


class PurchaseOder(models.Model):
    _inherit = 'purchase.order'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
    )


class PurchaseOderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_wht_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
        ondelete='restrict',
    )
