from odoo import models, fields


class AccountWhtType(models.Model):
    _inherit = "account.wht.type"

    account_id = fields.Many2one(
        string='WHT Account',
        comodel_name='account.account'
    )
