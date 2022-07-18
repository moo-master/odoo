from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_address = fields.Text('Address')

    x_partner_name = fields.Char(
        string='Partner Name',
        readonly=True,
    )
