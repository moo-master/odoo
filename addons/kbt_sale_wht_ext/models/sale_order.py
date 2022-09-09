from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_wht = fields.Float(
        string="WHT Amount",
        store=True,
        compute='_compute_wht_amount'
    )

    @api.depends('order_line.price_unit', 'order_line.wht_type_id')
    def _compute_wht_amount(self):
        for so in self:
            all_wht_in_lines = so.order_line.mapped(
                lambda x: x.price_subtotal * (x.wht_type_id.percent / 100))
            wht_2_decimal_digits = [round(each_element, 2)
                                    for each_element in all_wht_in_lines]
            so.amount_wht = format(round(sum(wht_2_decimal_digits), 2), '.2f')

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super()._create_invoices(grouped=grouped, final=final, date=date)
        for so in res.invoice_line_ids:
            so.wht_type_id = so.product_id.wht_type_id

        return res
