from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    ap_approver_uid = fields.Many2one(
        comodel_name='res.users',
        string='AP Approver'
    )
    ap_manager_uid = fields.Many2one(
        comodel_name='res.users',
        string='AP Menager'
    )
    ar_approver_uid = fields.Many2one(
        comodel_name='res.users',
        string='AR Approver'
    )
    ar_manager_uid = fields.Many2one(
        comodel_name='res.users',
        string='AR Menager'
    )
