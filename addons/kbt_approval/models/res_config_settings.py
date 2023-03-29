from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ap_approver_uid = fields.Many2one(
        comodel_name='res.users',
        string='AP Approver',
        related='company_id.ap_approver_uid',
        readonly=False,
    )
    ap_manager_uid = fields.Many2one(
        comodel_name='res.users',
        string='AP Manager',
        related='company_id.ap_manager_uid',
        readonly=False,
    )
    ar_approver_uid = fields.Many2one(
        comodel_name='res.users',
        string='AR Approver',
        related='company_id.ar_approver_uid',
        readonly=False,
    )
    ar_manager_uid = fields.Many2one(
        comodel_name='res.users',
        string='AR Manager',
        related='company_id.ar_manager_uid',
        readonly=False,
    )
