from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    # pylint: disable=biszx-relation2one-field-name
    issue_eid = fields.Many2one(
        comodel_name='hr.employee',
        string='Default Issue By',
    )
    # pylint: disable=biszx-relation2one-field-name
    approve_eid = fields.Many2one(
        comodel_name='hr.employee',
        string='Default Approve By',
    )
