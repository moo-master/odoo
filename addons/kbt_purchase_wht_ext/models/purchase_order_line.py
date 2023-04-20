from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.write({
            'wht_type_id': self.product_id.product_tmpl_id.purchase_wht_type_id.id
        })
