from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wht_type_id = fields.Many2one(
        'account.wht.type',
        string='Withholding Tax',
    )

    @api.onchange('detailed_type')
    def _onchange_detailed_type(self):
        for product in self:
            if product.detailed_type:
                product.wht_type_id = False
