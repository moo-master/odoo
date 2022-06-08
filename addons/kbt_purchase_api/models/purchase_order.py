from odoo import models, fields


class PurchaseOderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_wht_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
        ondelete='restrict',
    )
