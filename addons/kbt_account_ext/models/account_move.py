from odoo import models

from bahttext import bahttext


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_amount_total_text(self, amount):
        return bahttext(amount)
