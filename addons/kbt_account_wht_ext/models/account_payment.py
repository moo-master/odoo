from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    move_wht_id = fields.Many2one(
        comodel_name='account.move',
        string='Move with WHT'
    )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals)

        if self.move_wht_id:
            move = self.move_wht_id
            amount_wht = self.move_wht_id.amount_wht
            liquidity_line, receivable_payable = res
            liquidity_wht_line = liquidity_line.copy()

            type_val = 'debit' if self.payment_type == 'inbound' else 'credit'
            amount_val = liquidity_line[type_val]

            liquidity_line[type_val] = amount_val - amount_wht

            account_id = move.company_id.ar_wht_default_account_id
            if move.move_type != 'out_invoice':
                account_id = move.company_id.ap_wht_default_account_pnd3_id \
                    if move.partner_id.company_type == 'person' \
                    else move.company_id.ap_wht_default_account_pnd53_id

            liquidity_wht_line[type_val] = amount_wht
            liquidity_wht_line['account_id'] = account_id.id

            res = [liquidity_line, liquidity_wht_line, receivable_payable]

        return res
