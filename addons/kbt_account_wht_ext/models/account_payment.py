from odoo import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)

        sql = '''
            SELECT
                payment.id,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
                invoice.move_type
            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN %s
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            GROUP BY payment.id, invoice.move_type
        '''

        self._cr.execute(sql, (tuple(payments.ids),))
        query_res = self._cr.dictfetchall()

        move = self.env['account.move'].browse(
            query_res.get('invoice_ids', []))
        move_lines = move.invoice_line_ids.filtered('wht_type_id')

        for line in move_lines:
            account_id = move.company_id.ar_wht_default_account_pnd53_id
            if move.move_type == 'out_invoice':
                account_id = move.company_id.ar_wht_default_account_id
            elif move.partner_id.company_type == 'person':
                account_id = move.company_id.ar_wht_default_account_pnd3_id

            val_line_ids = {
                'invoice_line_id': line.id,
                'invoice_no': move.name,
                'wht_type_id': line.wht_type_id.id,
                'percent': line.wht_type_id.percent,
                'base_amount': line.price_subtotal,
                'wht_amount': line.amount_wht,
            }

            wht = self.env['account.wht'].create({
                'partner_id': move.partner_id.id,
                'wht_type': 'sale' if move.move_type == 'out_invoice'
                else 'purchase',
                'wht_payment': 'wht',
                'account_id': account_id.id,
                'line_ids': [(0, 0, val_line_ids)]
            })
            wht.action_done()

        return payments
