from odoo import models

from bahttext import bahttext


class AccountMove(models.Model):
    _inherit = 'account.move'

    def amount_total_text(self, amount):
        return bahttext(amount)
