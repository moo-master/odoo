from odoo import models, fields  # , api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_wht = fields.Float(
        string="WHT Amount",
        store=True,
        compute='_compute_wht_amount'
    )

    # @api.depends('order_line.price_unit', 'order_line.wht_type_id')
    # def _compute_wht_amount(self):
    #     for so in self:
    #         print("----------------------------------------------------------------------------------------------------------------------------")
    #         print(so.order_line.mapped(lambda x: x.price_unit*(x.wht_type_id.percent/100)))
    #         so.amount_wht = so.order_line.mapped('price_unit')

    # @api.model_create_multi
    # def create(self, vals_list):
    #     print("----------------------------------------------------------------------------------------------------------------------------")
    #     print(vals_list)
    #     unique_wht = []
    #     for each_val in vals_list[0].get('order_line'):
    #         if each_val[2].get('wht_type_id'):
    #             wht_type_id = self.env['account.wht.type'].search(
    #             [('id', '=', each_val[2].get('wht_type_id'))])
    #             check = 0
    #             for each_wht in unique_wht:
    #                 if each_wht[0].get('id') == each_val[2].get('wht_type_id'):
    #                     check += 1
    #                     each_wht[0]['total'] += 1
    #                     each_wht[0]['total_amount'] += each_val[2].get('price_unit')
    #                     break

    #             if check == 0:
    #                 unique_wht.append([{'id': each_val[2].get('wht_type_id'), 'total': 1, 'total_amount': each_val[2].get('price_unit')}])

    #     print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #     print(unique_wht)
    #     return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)
