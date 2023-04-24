from odoo import models, fields, api


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

    @api.model
    def create(self, vals):
        res = super(ResPartnerInherit, self).create(vals)
        if res.x_interface_id:
            res.ref = res.x_interface_id[0:16]
        return res
