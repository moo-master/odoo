from odoo import fields, models, _
from odoo.exceptions import ValidationError


class OffsetPaymentWizard(models.TransientModel):
    _name = 'offset.payment.wizard'

    account_id = fields.Many2one(
        'account.account',
        string='Offset Account',
        required=True
    )

    def button_confirm(self):
        move_ids = self.env['account.move'].browse(
            self.env.context.get('active_ids'))
        for move in move_ids:
            if move.total_offset > move.amount_total:
                raise ValidationError(
                    _("""Waning! This process cannot continues because the amount to be processed is greater than the amount of this document"""))
            if move.payment_state != 'not_paid':
                raise ValidationError(_(
                    """Document No. %(number)s cannot be processed because the payment has already been processed""",
                    number=move.name
                ))
