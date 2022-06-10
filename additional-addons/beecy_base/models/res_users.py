from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    signature = fields.Binary(
        string='Signature',
        copy=True,
    )
