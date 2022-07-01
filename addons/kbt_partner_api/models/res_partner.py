from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    x_interface_id = fields.Char(
        string='Partner Interface',
        readonly=True,
    )

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
    )

    def create(self):
        res = super().create()
        res.ref = res.x_interface_id
