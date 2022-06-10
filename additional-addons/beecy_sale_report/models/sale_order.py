from odoo import models
from bahttext import bahttext


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _amount_total_text(self, amount):
        return bahttext(amount)
