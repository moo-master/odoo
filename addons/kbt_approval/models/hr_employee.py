from odoo import models, fields


class OrgLevelLine(models.Model):
    _inherit = 'hr.employee'

    level_id = fields.Many2one(
        string='Level',
        comodel_name='org.level',
        ondelete='restrict',
    )
