from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    issue_uid = fields.Many2one(
        comodel_name='res.users',
        string='Default Issue By',
        related='company_id.issue_uid',
        readonly=False,
    )
    approve_uid = fields.Many2one(
        comodel_name='res.users',
        string='Default Approve By',
        related='company_id.approve_uid',
        readonly=False,
    )
