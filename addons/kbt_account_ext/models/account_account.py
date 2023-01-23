from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_group_id = fields.Many2one(
        'account.account.group',
        string='Account Group',
    )
