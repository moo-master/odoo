from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_address = fields.Text('Address')
