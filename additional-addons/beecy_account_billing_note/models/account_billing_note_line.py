from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountBillingNoteLine(models.Model):
    _name = 'account.billing.note.line'
    _description = 'Billing Note Lines'

    billing_note_id = fields.Many2one(
        comodel_name='account.billing.note',
        string='Billing Note',
        copy=False,
        index=True,
        ondelete='cascade',
    )

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        copy=False,
        index=True,
        ondelete='cascade',
    )

    note = fields.Html(
        string='Note',
        related='invoice_id.narration'
    )

    invoice_payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Term",
        related='invoice_id.invoice_payment_term_id',
    )

    invoice_date = fields.Date(
        string="Date Invoice",
        related='invoice_id.invoice_date',
    )

    invoice_due_date = fields.Date(
        string="Due Date",
        related='invoice_id.invoice_date_due',
    )

    currency_id = fields.Many2one(
        string='Currency',
        related='invoice_id.currency_id',
    )

    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )

    balance = fields.Monetary(
        string='Balance',
        currency_field='currency_id',
    )

    wht_total = fields.Float(
        string='WHT Total',
    )

    paid_amount = fields.Float(
        string='Paid Amount',
    )
    is_billing = fields.Boolean(
        default=True,
    )

    @api.onchange("invoice_id")
    def _onchange_invoice_id(self):
        for rec in self:
            rec.paid_amount = rec.invoice_id.amount_residual

    @api.onchange("paid_amount")
    def _onchange_paid_amount(self):
        if self.paid_amount > self.balance:
            raise ValidationError(_('Error!\nThe paid amount over balance.'))

    def button_unbill(self):
        for rec in self:
            bills = rec.invoice_id.billing_note_ids.filtered(
                lambda r: r.id == rec.billing_note_id.id and rec.invoice_id.id in r.invoice_id.ids)
            if bills:
                for bill in bills:
                    rec.invoice_id.write({
                        'billing_note_ids': [(3, bill.id)],
                    })
            rec.is_billing = False
