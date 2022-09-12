from odoo import models, fields

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

    def get_amount_total_text(self, amount):
        return bahttext(amount)
