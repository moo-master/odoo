from odoo import models


class SaleMakeInvoiceAdvance(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # def _create_invoice(self, order, so_line, amount):
    #     print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    #     return super()._create_invoice(order, so_line, amount)

    # def create_invoices(self):
    #     res = super().create_invoices()
    #     print("----------------------------------------------------------------------------------------------------------------------------")
    #     print(res.get('res_id'))

    #     return res
