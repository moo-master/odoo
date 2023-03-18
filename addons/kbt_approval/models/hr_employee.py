from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    level_id = fields.Many2one(
        string='Level',
        comodel_name='org.level',
        ondelete='restrict',
    )
    is_send_email = fields.Boolean(
        string='Email Notification',
    )
    ap_approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='AP Approver',
        domain="['|', "
               "('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    ar_approver_id = fields.Many2one(
        comodel_name='hr.employee',
        string='AR Approver',
        domain="['|', "
               "('company_id', '=', False), ('company_id', '=', company_id)]",
    )
