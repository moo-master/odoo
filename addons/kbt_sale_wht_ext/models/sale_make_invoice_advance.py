from odoo import models


class SaleMakeInvoiceAdvance(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # def create_invoices(self):
    #     print("----------------------------------------------------------------------------------------------------------------------------")
    #     print(order)
    #     print(so_line)
    #     print(amount)

    #     return super().create_invoices()
