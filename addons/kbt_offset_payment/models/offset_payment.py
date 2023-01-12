from odoo import fields, models


class OffsetPayment(models.Model):
    _name = 'offset.payment'

    move_id = fields.Many2one(
        comodel_name='account.move'
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice/Bill',
        required=True,
        domain=[
            ('payment_state', '=', 'not_paid'),
            ('partner_id.x_offset', '=', True)
        ]
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        related='invoice_id.partner_id'
    )
    invoice_date = fields.Date(
        string='Invoice Date',
        related='invoice_id.invoice_date'
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='invoice_id.currency_id'
    )
    amount_untaxed = fields.Monetary(
        string='Tax Excluded',
        related='invoice_id.amount_untaxed',
        currency_field='company_currency_id'
    )
    total_amount = fields.Monetary(
        string='Amount',
        related='invoice_id.amount_total',
        currency_field='company_currency_id'
    )
