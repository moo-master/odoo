from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_branch_name = fields.Char(
        string='X Branch Name',
    )
