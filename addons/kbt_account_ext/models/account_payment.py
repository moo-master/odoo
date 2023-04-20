from odoo import models
from bahttext import bahttext


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _amount_total_text(self, amount):
        return bahttext(amount)
