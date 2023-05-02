from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    signature = fields.Binary(
        string='Signature',
        copy=True,
    )
