from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(
            SaleOrderLine,
            self)._prepare_invoice_line(
            **optional_values)
        order = self.order_id
        if order.x_is_interface and order.invoice_count > 0 and order.so_type_id.is_unearn_revenue:
            res['account_id'] = order.so_type_id.x_revenue_account_id
        return res
