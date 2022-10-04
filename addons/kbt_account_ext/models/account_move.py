from odoo import models, fields, api

from bahttext import bahttext


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_type = fields.Selection(
        selection_add=[
            ('in_refund', 'Debit Note'),
            ('out_refund', 'Credit Note'),
        ],
        ondelete={'in_refund': 'set default', 'out_refund': 'set default'}
    )
    x_old_invoice_amount = fields.Float(
        string='Old Invoice Amount',
        compute='_compute_old_invoice_amount',
        store=True,
    )
    x_wht_amount = fields.Float(
        string='WHT Amount',
        compute='_compute_old_invoice_amount',
        store=True,
    )
    x_real_amount = fields.Float(
        string='Real Amount',
    )
    x_diff_amount = fields.Float(
        string='Diff Amount',
    )

    def get_amount_total_text(self, amount):
        return bahttext(amount)

    @api.depends('x_real_amount')
    def _compute_old_invoice_amount(self):
        for move in self:
            move_id = move.reversed_entry_id
            move.write({
                'x_old_invoice_amount': move_id.amount_untaxed,
                'x_diff_amount': move.x_old_invoice_amount - move.x_real_amount,
                'x_wht_amount': move_id.amount_wht,
            })

    @api.onchange('x_real_amount')
    def _onchange_x_real_amount(self):
        self.write({
            'x_diff_amount': self.x_old_invoice_amount - self.x_real_amount
        })
