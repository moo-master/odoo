from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _create_account_payment(self, line_invoice, billing_note):
        res = super(AccountMove, self)._create_account_payment(
            line_invoice, billing_note)
        res._onchange_create_temp_journal_item()
        return res
