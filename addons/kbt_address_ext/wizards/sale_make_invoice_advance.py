from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        move = super()._create_invoice(order, so_line, amount)
        move.write({
            'x_address': order.x_address,
            'x_partner_name': order.x_partner_name,
        })
        return move
