from odoo import models, fields, api, _
from math import copysign


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    move_wht_ids = fields.Many2many(
        comodel_name='account.move',
        relation='account_payment_account_move_wht_rel',
        column1='payment_id',
        column2='move_id',
        string='Move with WHT',
    )
    wht_ids = fields.One2many(
        'account.wht',
        'payment_id',
        'Withholding Tax'
    )
    wht_count = fields.Integer(
        'WHT count',
        compute='_compute_wht_count',
        default=0
    )

    @api.depends('wht_ids')
    def _compute_wht_count(self):
        for rec in self:
            rec.wht_count = len(rec.wht_ids)
            return

    def button_open_wht(self):
        ''' Redirect the user to the wht(s) paid by this payment.
        :return:    An action on account.wht.
        '''
        self.ensure_one()

        action = {
            'name': _("Paid Withholding Tax"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.wht',
            'context': {'create': False},
        }
        if len(self.wht_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.wht_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.wht_ids.ids)],
            })
        return action

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res: list = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals)

        # account.move.line with wht
        wht_lines = self.move_wht_ids.invoice_line_ids.filtered('wht_type_id')
        for line in wht_lines:
            move = line.move_id
            amount_wht = line.amount_wht

            liquidity_line = res[0]
            liquidity_wht_line = liquidity_line.copy()

            type_val = 'debit' if self.payment_type == 'inbound' else 'credit'
            amount_val = liquidity_line[type_val]

            liquidity_line[type_val] = amount_val - amount_wht
            liquidity_line['amount_currency'] = \
                copysign(1, liquidity_line['amount_currency']) *\
                (amount_val - amount_wht)

            account_id = move.company_id.ar_wht_default_account_id
            if move.move_type != 'out_invoice':
                account_id = move.company_id.ap_wht_default_account_pnd3_id \
                    if move.partner_id.company_type == 'person' \
                    else move.company_id.ap_wht_default_account_pnd53_id

            liquidity_wht_line[type_val] = amount_wht
            liquidity_wht_line['amount_currency'] = amount_wht
            liquidity_wht_line['account_id'] = account_id.id
            liquidity_wht_line['is_wht_line'] = True
            liquidity_wht_line['wht_type_id'] = line.wht_type_id.id

            res.append(liquidity_wht_line)

        return res

    def _seek_for_lines(self):
        liquidity_lines, counterpart_lines, writeoff_lines = super()._seek_for_lines()
        writeoff_lines = writeoff_lines.filtered(lambda x: not x.is_wht_line)
        return liquidity_lines, counterpart_lines, writeoff_lines
