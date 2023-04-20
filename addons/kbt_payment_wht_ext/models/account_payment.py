from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    wht_payment_date = fields.Date(
        string='WHT Payment Date',
    )

    def action_draft(self):
        moves = self.reconciled_bill_ids or self.reconciled_invoice_ids
        moves.update({'is_wht_paid': False})
        return super().action_draft()

    def action_cancel(self):
        res = super().action_cancel()
        wht_ids = self.env['account.wht'].search(
            [('payment_id', '=', self.id)])
        for wht in wht_ids:
            wht.action_cancel()
        return res
