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
    wht_payment_date = fields.Date(
        string='WHT Payment Date',
        default=fields.Date.today(),
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
        if move.mapped('amount_wht') and any(
                move.mapped(lambda x: not x.partner_id.vat)):
            raise ValidationError(
                _('This contact has not Tax ID, You should fill the Tax ID in the Contact Module'))

        if self.amount < self.wht_amount:
            raise ValidationError(
                _('Amount must greater or equal to WHT Amount')
            )

        move.update({'is_wht_paid': True})
        return res

    @api.depends('line_ids')
    def _compute_from_lines(self):
        for wizard in self:
            res = super(AccountPaymentRegister, wizard)._compute_from_lines()
            if self.wht_amount > 0:
                wizard.can_group_payments = False
            return res
