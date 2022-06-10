from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )
