from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    issue_uid = fields.Many2one(
        comodel_name='res.users',
        string='Default Issue By'
    )
    approve_uid = fields.Many2one(
        comodel_name='res.users',
        string='Default Approve By'
    )
