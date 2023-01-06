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
