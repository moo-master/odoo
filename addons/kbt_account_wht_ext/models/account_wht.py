from odoo import fields, models


class AccountWht(models.Model):
    _inherit = 'account.wht'

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment'
    )
