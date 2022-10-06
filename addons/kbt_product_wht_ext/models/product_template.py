from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
    )
