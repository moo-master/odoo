from odoo import fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class OffsetPaymentWizard(models.TransientModel):
    _name = 'offset.payment.wizard'

    account_id = fields.Many2one(
        'account.account',
        string='Offset Account',
        required=True
    )

    def _get_type(self, move_type):
        return ('inbound', 'customer') if move_type == 'out_invoice' \
            else ('outbound', 'supplier')

    def _get_bank_journal(self):
        return self.env['account.journal'].search(
            [('code', '=', 'BNK')], limit=1)

    def _get_manual_payment_method(self, journal_id, payment_type):
        journal = journal_id._get_available_payment_method_lines(payment_type)
        journal = journal.filtered(lambda a: a.code == 'manual')
        return journal

    def _reconcile_payments(self, move_line, payment_line_ids):
        domain = [('account_internal_type', 'in',
                   ('receivable', 'payable')), ('reconciled', '=', False)]
        payment_lines = payment_line_ids.filtered_domain(domain)
        for account in payment_lines.account_id:
            (payment_lines + move_line).filtered_domain([
                ('account_id', '=', account.id),
                ('reconciled', '=', False)
            ]).reconcile()

    def _prepare_wht_line_ids(self, line):
        return {
            'invoice_line_id': line.id,
            'invoice_no': line.move_id.name,
            'wht_type_id': line.wht_type_id.id,
            'percent': line.wht_type_id.percent,
            'base_amount': line.price_subtotal,
            'wht_amount': line.amount_wht,
        }

    def link_wht(self, payments):
        move_type = payments.reconciled_bill_ids \
            or payments.reconciled_invoice_ids

        moves = move_type.filtered('invoice_line_ids.wht_type_id')

        for move in moves:
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

    def button_confirm(self):
        move_ids = self.env['account.move'].browse(
            self.env.context.get('active_ids'))
        for move in move_ids:
            if move.total_offset > move.amount_residual:
                raise ValidationError(
                    _("""Waning! This process cannot continues because the amount to be processed is greater than the amount of this document"""))
            payment_type = 'inbound' if move.move_type == 'out_invoice' else 'outbound'
            partner_type = 'customer' if move.move_type == 'out_invoice' else 'supplier'
            journal_id = self._get_bank_journal()
            payment_method_line_id = self._get_manual_payment_method(
                journal_id, payment_type)
            move_payment_val = {
                'move_wht_id': move.id if move.amount_wht else False,
                'payment_type': payment_type,
                'partner_type': partner_type,
                'partner_id': move.partner_id.id,
                'amount': move.amount_residual,
                'ref': 'Payment of ' + move.name,
                'journal_id': journal_id.id,
                'currency_id': move.currency_id.id,
                'payment_method_line_id': payment_method_line_id.id,
                'date': datetime.today(),
                'partner_bank_id': None,
                'destination_account_id': move.partner_id.property_account_receivable_id.id if partner_type == 'customer'
                else move.partner_id.property_account_payable_id.id
            }
            payment = self.env['account.payment'].with_context(
                default_invoice_ids=[(4, move.id, False)],
                offset_account_id=self.account_id,
                offset_amount=move.total_offset
            )
            move_payment = payment.create(move_payment_val)
            move_payment.action_post()
            self._reconcile_payments(move.line_ids, move_payment.line_ids)
            self.link_wht(move_payment)
            if move.offset_ids:
                for offset in move.offset_ids:
                    invoice = offset.invoice_id
                    if invoice.payment_state != 'not_paid':
                        raise ValidationError(_(
                            """Document No. %(number)s cannot be processed because the payment has already been processed""",
                            number=move.name
                        ))
                    payment_type = 'inbound' if invoice.move_type == 'out_invoice' else 'outbound'
                    partner_type = 'customer' if invoice.move_type == 'out_invoice' else 'supplier'
                    payment_method_line_id = self._get_manual_payment_method(
                        journal_id, payment_type)
                    offset_payment_val = {
                        'move_wht_id': move.id if move.amount_wht else False,
                        'payment_type': payment_type,
                        'partner_type': partner_type,
                        'partner_id': invoice.partner_id.id,
                        'amount': invoice.amount_residual,
                        'ref': 'Payment of ' + invoice.name,
                        'journal_id': journal_id.id,
                        'currency_id': invoice.currency_id.id,
                        'payment_method_line_id': payment_method_line_id.id,
                        'date': datetime.today(),
                        'partner_bank_id': None,
                        'destination_account_id': invoice.partner_id.property_account_receivable_id.id if partner_type == 'customer'
                        else invoice.partner_id.property_account_payable_id.id
                    }
                    payment = self.env['account.payment'].with_context(
                        default_invoice_ids=[(4, invoice.id, False)],
                        offset_account_id=self.account_id
                    )
                    invoice_payment = payment.create(offset_payment_val)
                    invoice_payment.action_post()
                    self._reconcile_payments(
                        invoice.line_ids, invoice_payment.line_ids)
                    self.link_wht(invoice_payment)

                move.write({'x_offset': True})
