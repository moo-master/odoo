from odoo import models, fields, api


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    # pylint: disable=biszx-boolean-field-name
    x_offset = fields.Boolean(
        string='Offset Payment',
        related='move_id.partner_id.x_offset',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for each_val in vals_list:
            if each_val.get('display_type') == 'line_note':
                each_val['account_id'] = False
        super().create(vals_list)
