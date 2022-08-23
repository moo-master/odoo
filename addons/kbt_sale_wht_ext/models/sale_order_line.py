from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
        default=lambda self: self.product_id.product_tmpl_id.wht_type_id
    )
