from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type',
    )

    @api.onchange('detailed_type')
    def _onchange_detailed_type(self):
        # ORVERIDE from beecy_account_wht
        for product in self:
            if product.detailed_type != 'service':
                product.write({
                    'purchase_wht_type_id': False,
                    'wht_type_id': False,
                })
