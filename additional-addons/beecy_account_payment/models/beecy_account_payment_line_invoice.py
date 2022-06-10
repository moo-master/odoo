from odoo import models, fields


class AccountPaymentLineInvoice(models.Model):
    _name = 'account.payment.line.invoice'
    _description = 'List of invoices to payment'
    _rec_name = 'invoice_id'

    payment_id = fields.Many2one(
        comodel_name='beecy.account.payment',
        string='Account Payment',
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
    invoice_date_due_date = fields.Date(
        string="Due Date",
        related='invoice_id.invoice_date_due',
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        related='invoice_id.amount_untaxed',
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        related='invoice_id.amount_total',
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related='invoice_id.currency_id',
    )
    amount_wht = fields.Monetary(
        string="Amount WHT",
        related_sudo='invoice_id.amount_wht',
    )
    amount_residual = fields.Monetary(
        string="Balance",
        related='invoice_id.amount_residual',
    )
    amount_tobe_paid = fields.Float(
        string='Paid',
    )
