from odoo import models, fields


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    # pylint: disable=biszx-boolean-field-name
    x_offset = fields.Boolean(
        string='Offset Payment',
        related='move_id.partner_id.x_offset',
        store=True,
    )
