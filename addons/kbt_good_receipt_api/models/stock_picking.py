from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'stock.picking'

    x_bill_date = fields.Date(
        string='Bill Date',
        readonly=True,
    )

    x_bill_reference = fields.Char(
        string='Bill Reference',
        readonly=True,
    )
