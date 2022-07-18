from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_bill_ref = fields.Char('X Bill ref')
    x_bill_date = fields.Date('X Bill Date')
