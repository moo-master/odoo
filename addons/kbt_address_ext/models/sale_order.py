from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_address = fields.Text('Address')

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices()
        res.write({
            'x_address': self.x_address
        })
        return res
