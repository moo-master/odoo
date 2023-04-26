from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_exempt = fields.Boolean(
        string='is Exempt'
    )
