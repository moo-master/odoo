from odoo import fields, models


class AccountInvoiceWizard(models.TransientModel):
    _name = 'account.invoice.wizard'
    _description = 'Account Invoice Wizard'

    billing_note_id = fields.Many2one(
        comodel_name='account.billing.note',
        string='Billing Note',
    )

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        copy=False,
    )

    invoice_due_date = fields.Date(
        string="Due Date",
        related='invoice_id.invoice_date_due',
    )

    currency_id = fields.Many2one(
        string='Currency',
        related='invoice_id.currency_id',
    )

    amount_untaxed_signed = fields.Monetary(
        string='Tax Excluded',
        currency_field='currency_id',
        related='invoice_id.amount_untaxed_signed',
    )

    amount_total_signed = fields.Monetary(
        string='Total',
        currency_field='currency_id',
        related='invoice_id.amount_total_signed',
    )

    payment_state = fields.Selection(
        string='Payment Status',
        related='invoice_id.payment_state',
    )

    move_type = fields.Selection(
        string='Type',
        related='invoice_id.move_type',
    )

    paid_amount = fields.Float(
        string='Paid Amount',
    )

    def action_confirm_invoice(self):
        invoice = []
        billing_note_obj = self.env['account.billing.note'].browse(
            self.billing_note_id.id
        )
        for line in self:
            paid_amount = line.paid_amount
            amount = line.invoice_id.amount_total
            balance = line.invoice_id.amount_residual
            wht_total = line.invoice_id.amount_wht
            if line.move_type == 'out_refund':
                paid_amount = abs(paid_amount) * -1
                amount = abs(amount) * -1
                balance = abs(balance) * -1
                wht_total = abs(wht_total) * -1
            val = (0, 0, {
                'invoice_id': line.invoice_id.id,
                'billing_note_id': line.billing_note_id.id,
                'paid_amount': paid_amount,
                'wht_total': wht_total,
                'amount': amount,
                'balance': balance,
            })
            invoice.append(val)
        billing_note_obj.update({'line_ids': invoice})
