from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    wht_amount = fields.Float(
        string='WHT Amount',
    )
    paid_amount = fields.Float(
        string='Paid Amount',
    )

    @api.onchange('paid_amount')
    def _onchange_paid_amount(self):
        for wizard in self:
            wizard.write({
                'amount': wizard.paid_amount + wizard.wht_amount
            })

    def action_create_payments(self):
        res = super().action_create_payments()

        ctx = dict(self.env.context)
        move = self.env['account.move'].browse(ctx.get('active_ids'))
        if self.amount < self.wht_amount:
            raise ValidationError(
                _('Amount must greater or equal to WHT Amount')
            )

        move.update({'is_wht_paid': True})
        return res
