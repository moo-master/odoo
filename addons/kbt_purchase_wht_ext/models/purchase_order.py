from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)
