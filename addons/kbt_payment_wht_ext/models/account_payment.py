from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_draft(self):
        moves = self.reconciled_bill_ids or self.reconciled_invoice_ids
        moves.update({'is_wht_paid': False})
        return super().action_draft()
