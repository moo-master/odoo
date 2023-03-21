from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    wht_payment_date = fields.Date(
        string='Wht Payment Date',
    )

    def action_draft(self):
        moves = self.reconciled_bill_ids or self.reconciled_invoice_ids
        moves.update({'is_wht_paid': False})
        return super().action_draft()
