
from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    account_entry = fields.Selection(
        string='Account Entries',
        selection=[
            ('ap', 'Account Payable'),
            ('ar', 'Account Receivable')
        ]
    )
