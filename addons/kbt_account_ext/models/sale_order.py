from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(
            SaleOrderLine,
            self)._prepare_invoice_line(
            **optional_values)
        if self.order_id.x_is_interface:
            res['account_id'] = self.order_id.so_type_id.x_revenue_account_id
        return res
