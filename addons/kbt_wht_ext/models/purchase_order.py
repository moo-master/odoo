from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        inverse_name='purchase_id',
        readonly=True
    )
