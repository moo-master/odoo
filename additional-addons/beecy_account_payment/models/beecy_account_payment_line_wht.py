from odoo import models, fields


class AccountPaymentLineWht(models.Model):
    _name = 'account.payment.line.wht'
    _description = 'List of witholding tax'
    _rec_name = 'invoice_line_id'

    payment_id = fields.Many2one(
        comodel_name='beecy.account.payment',
        string='Account Payment',
        copy=False,
        index=True,
        ondelete='cascade',
    )
    invoice_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Invoice Line',
        copy=False,
        index=True,
        ondelete='cascade',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        related='invoice_line_id.move_id',
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related='invoice_id.currency_id',
    )
    wht_type_id = fields.Many2one(
        comodel_name='account.wht.type',
        string='WHT',
    )
    percent = fields.Float(
        string='Percent',
    )
    price_subtotal = fields.Monetary(
        string='Base',
        store=True,
        readonly=True,
        currency_field='currency_id',
        related='invoice_line_id.price_subtotal',
    )
    # price_subtotal, related มาจาก invoice_line_id
    # FYI. Base คือ (unit_price * qty) - discount - prorate
    amount_wht = fields.Monetary(
        string='Total',
        currency_field='currency_id',
    )
    note = fields.Text(
        string='Note',
    )
