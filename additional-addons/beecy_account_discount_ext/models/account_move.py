from functools import reduce

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_type = fields.Selection(
        selection_add=[
            ('out_debit', 'Customer Debit Note'),
            ('in_debit', 'Vendor Debit Note'),
        ],
        ondelete={'out_debit': 'set default', 'in_debit': 'set default'}
    )

    formula_discount = fields.Char(
        string='Disc. %',
    )

    direct_discount = fields.Float(
        string='Disc. Amount',
        digits='Discount',
        default=0
    )

    @api.model
    def _get_price_discount_model(self, price_unit=0.0, formula=''):
        return reduce(
            lambda x, y: x * y,
            [price_unit] + self._get_ordered_factor(formula=formula)
        )

    @api.model
    def _get_price_wo_discount_model(self, price_unit=0.0, formula=''):
        return reduce(
            lambda x, y: x / y,
            [price_unit] + self._get_ordered_factor(formula=formula)
        )

    @staticmethod
    def _get_ordered_factor(formula):
        def _isfloat(num_str):
            try:
                float(num_str)
                return True
            except ValueError:
                return False

        formula = str(formula) if formula else ''

        return [
            1 - (j * 0.01)
            for j in map(
                float, filter(
                    _isfloat, ",".join(
                        formula.replace('%', ' ').split('+')
                    ).split(',')
                )
            )
            if j < 100
        ]
