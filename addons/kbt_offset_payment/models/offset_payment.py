from odoo import fields, models, api


class OffsetPayment(models.Model):
    _name = 'offset.payment'
    _description = 'Offset Payment'

    move_id = fields.Many2one(
        comodel_name='account.move'
    )
    offset_move_type = fields.Char(
        compute='_compute_move_type'
    )
    move_partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='move_id.partner_id'
    )
    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice/Vendor Bill',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer/Vendor',
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
    total_amount_due = fields.Monetary(
        string='Amount Due',
        related='invoice_id.amount_residual',
        currency_field='company_currency_id'
    )
    total_amount = fields.Monetary(
        string='Amount Total',
        related='invoice_id.amount_total',
        currency_field='company_currency_id'
    )

    @api.depends('move_id')
    def _compute_move_type(self):
        if self.move_id.move_type == 'out_invoice':
            self.offset_move_type = 'in_invoice'
        if self.move_id.move_type == 'in_invoice':
            self.offset_move_type = 'out_invoice'
