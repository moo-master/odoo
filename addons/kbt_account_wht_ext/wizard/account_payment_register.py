from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        payments = super()._create_payments()

        move_type = payments.reconciled_bill_ids \
            or payments.reconciled_invoice_ids

        moves = move_type.filtered('invoice_line_ids.wht_type_id')

        for move in moves.filtered(lambda x: not x.is_wht_paid):
            account_id = move.company_id.ar_wht_default_account_id
            if move.move_type != 'out_invoice':
                account_id = move.company_id.ap_wht_default_account_pnd3_id \
                    if move.partner_id.company_type == 'person' \
                    else move.company_id.ap_wht_default_account_pnd53_id

            line_ids_lst = [
                (0, 0, self._prepare_wht_line_ids(line))
                for line in move.invoice_line_ids.filtered('wht_type_id')
            ]

            wht = self.env['account.wht'].create({
                'partner_id': move.partner_id.id,
                'wht_kind': 'pnd3' if move.partner_id.company_type == 'person'
                else 'pnd53',
                'wht_type': 'sale' if move.move_type == 'out_invoice'
                else 'purchase',
                'wht_payment': 'wht',
                'account_id': account_id.id,
                'document_date': fields.Datetime.now(),
                'line_ids': line_ids_lst,
            })
            wht.action_done()
            payments.write({
                'wht_ids': [(4, wht.id)]
            })

        return payments

    def _prepare_wht_line_ids(self, line):
        return {
            'invoice_line_id': line.id,
            'invoice_no': line.move_id.name,
            'wht_type_id': line.wht_type_id.id,
            'percent': line.wht_type_id.percent,
            'base_amount': line.price_subtotal,
            'wht_amount': line.amount_wht,
        }

    def _init_payments(self, to_process, edit_mode=False):

        for data in to_process:
            # Select reconcile account move line to find move_id
            move_id = data['to_reconcile'].move_id.filtered(
                lambda x: not x.is_paid_wht)
            if move_id.amount_wht:
                data['create_vals'].update({
                    'move_wht_ids': [(6, 0, move_id.ids)]
                })

        payments = super()._init_payments(to_process, edit_mode=edit_mode)

        return payments
