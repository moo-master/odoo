from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_wht_paid = fields.Boolean(
        string='WHT Paid',
        readonly=True,
        copy=False,
        default=False,
    )

    def action_register_payment(self):
        res = super().action_register_payment()
        amount_wht = 0 if self.is_wht_paid else self.amount_wht
        res['context'].update({
            'default_wht_amount': amount_wht,
            'default_paid_amount': self.amount_residual - amount_wht,
        })

        return res

    def button_draft(self):
        self.write({'is_wht_paid': False})
        return super().button_draft()
