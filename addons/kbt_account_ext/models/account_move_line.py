from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_group_id = fields.Many2one(
        'account.account.group',
        string='Account Group',
        related='account_id.account_group_id',
        store=True,
    )
