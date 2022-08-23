from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
        default='product_id.purchase_wht_type_id'
    )
