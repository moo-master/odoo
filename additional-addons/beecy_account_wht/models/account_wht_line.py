from odoo import fields, models, api
import decimal


class AccountWhtLine(models.Model):
    _name = 'account.wht.line'
    _description = 'Account WHT Lines'

    @api.depends('percent', 'base_amount')
    def _compute_tax(self):
        for data in self:
            total = round((((data.percent / 100) or 0.0)
                           * data.base_amount), 2) or 0.0
            tax = decimal.Decimal(str(total)).quantize(
                decimal.Decimal('.01'), rounding=decimal.ROUND_UP)
            data.tax = tax

    wht_id = fields.Many2one(
        'account.wht',
    )
    invoice_line_id = fields.Many2one(
        'account.move.line',
        store=True,
        string='Invoice',
    )
    invoice_no = fields.Char(
        related='invoice_line_id.move_id.name',
    )
    wht_type_id = fields.Many2one(
        'account.wht.type',
        string='WHT Type'
    )
    percent = fields.Float(
        string='Percent',
        related='wht_type_id.percent',
    )
    base_amount = fields.Float(
        string='Base Amount',
        compute='_compute_base_amount',
    )
    wht_amount = fields.Float(
        'WHT Amount',
        compute='_compute_wht_amount',
    )
    note = fields.Char(
        string='Note',
    )
    tax = fields.Float(
        string='Tax Amount',
        compute="_compute_tax",
        digits='Account',
    )

    @api.depends('invoice_line_id.price_subtotal')
    def _compute_base_amount(self):
        for rec in self:
            rec.base_amount = rec.invoice_line_id.price_subtotal or 0.0

    @api.depends('base_amount', 'percent')
    def _compute_wht_amount(self):
        for rec in self:
            rec.wht_amount = abs(
                rec.invoice_line_id.amount_currency) * (rec.percent / 100.0)

    @api.onchange('invoice_line_id')
    def _onchange_wht_type_id(self):
        for rec in self:
            rec.wht_type_id = rec.invoice_line_id.wht_type_id.id
            rec.note = rec.wht_type_id.percent
