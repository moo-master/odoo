from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # pylint: disable=biszx-boolean-field-name
    x_offset = fields.Boolean(
        string='Offset Payment',
    )
