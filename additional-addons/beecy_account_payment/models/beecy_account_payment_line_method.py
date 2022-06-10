from odoo import models, fields, api


class AccountPaymentLineMethod(models.Model):
    _name = 'account.payment.line.method'
    _description = 'Payment via methods'
    _rec_name = 'payment_id'

    payment_id = fields.Many2one(
        comodel_name='beecy.account.payment',
        string='Account Payment',
        copy=False,
        index=True,
        ondelete='cascade',
    )
    payment_method_line_id = fields.Many2one(
        comodel_name='account.payment.method.line',
        string='Method',
        domain=lambda self: self._domain_payment_method_id(),
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related='payment_id.currency_id',
    )

    amount_total = fields.Monetary(
        string="Amount Total",
        required=True,
    )
    note = fields.Text(
        string='Note',
    )

    @api.model
    def _domain_payment_method_id(self):
        ctx = dict(self.env.context)
        payment_type = ctx.get('default_payment_type') or False
        return [('payment_type', '=', payment_type)]

    @api.onchange('payment_method_line_id')
    def _onchange_methods_ids(self):
        amount_total = (
            self.payment_id.amount_tobe_paid - self.payment_id.amount_wht
        )
        self.write({
            'amount_total': amount_total or 0.0,
        })
