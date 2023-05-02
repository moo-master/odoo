from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # pylint: disable=biszx-relation2one-field-name
    issue_eid = fields.Many2one(
        comodel_name='hr.employee',
        string='Default Issue By',
        related='company_id.issue_eid',
        readonly=False,
    )
    # pylint: disable=biszx-relation2one-field-name
    approve_eid = fields.Many2one(
        comodel_name='hr.employee',
        string='Default Approve By',
        related='company_id.approve_eid',
        readonly=False,
    )
