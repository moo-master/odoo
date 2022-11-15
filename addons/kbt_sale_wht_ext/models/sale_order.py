from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        for o_line in self.order_line:
            for i_line in o_line.invoice_lines:
                if o_line.wht_type_id:
                    i_line.wht_type_id = o_line.wht_type_id.id
                else:
                    i_line.wht_type_id = o_line.product_id.wht_type_id.id

        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            section_5_list = []
            section_6_list = []
            for line in rec.order_line:
                if (self.section_check(line.wht_type_id.sequence) == 5
                        and line.wht_type_id.id not in section_5_list):
                    section_5_list.append(line.wht_type_id.id)
                if (self.section_check(line.wht_type_id.sequence) == 6
                        and line.wht_type_id.id not in section_6_list):
                    section_6_list.append(line.wht_type_id.id)
            if len(section_5_list) > 1 or len(section_6_list) > 1:
                raise ValidationError(
                    _("You can not select different WHT under the same category."
                      " Right now your section 5 or section 6"
                      " are under the same category."))
        return res

    def section_check(self, sequence):
        if(int(sequence / 500) == 1 and (sequence % 500) < 100):
            return 5
        if(int(sequence / 600) == 1 and (sequence % 600) < 100):
            return 6
