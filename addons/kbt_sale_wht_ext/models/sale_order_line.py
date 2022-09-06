from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.write({
            'wht_type_id': self.product_id.product_tmpl_id.wht_type_id.id
        })
