from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        readonly=True
    )

    amount_wht = fields.Float(
        string="WHT Amount",
        store=True,
        compute='_compute_wht_amount'
    )

    @api.depends('order_line.price_unit', 'order_line.wht_type_id')
    def _compute_wht_amount(self):
        for po in self:
            all_wht_in_lines = po.order_line.mapped(
                lambda x: x.price_unit * (x.wht_type_id.percent / 100))
            wht_2_decimal_digits = [round(each_element, 2)
                                    for each_element in all_wht_in_lines]
            po.amount_wht = format(round(sum(wht_2_decimal_digits), 2), '.2f')

    # def action_create_invoice(self):
    #     res = super().action_create_invoice()
    #     print("------------------------------------------------------------------------------------------------------")
    #     wht_data = self.env['account.move'].search([
    #         ('id', '=', res.get('res_id'))
    #     ])
    #     print(wht_data.invoice_line_ids.wht_type_id)
    #     return res
