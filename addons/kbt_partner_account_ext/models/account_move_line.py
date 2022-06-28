from odoo import models, fields


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    # pylint: disable=biszx-compute-func-name,biszx-boolean-field-name
    x_offset = fields.Boolean(
        string='Offset Payment',
        compute='move.partner_id.x_offset',
        store=True,
    )
