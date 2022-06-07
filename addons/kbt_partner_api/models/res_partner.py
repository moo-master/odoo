from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    x_interface_id = fields.Char(
        string='Partner Interface',
        readonly=True,
    )
