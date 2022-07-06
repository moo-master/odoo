from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_address = fields.Text('Address')
