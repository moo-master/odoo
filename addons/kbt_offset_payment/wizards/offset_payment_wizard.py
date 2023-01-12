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
        return 'inbound', 'customer' if move_type == 'out_invoice' else 'outbound', 'supplier'

    def _get_bank_journal(self):
        return self.env['account.journal'].search(
            [('code', '=', 'BNK')], limit=1)

    def _get_manual_payment_method(self, journal_id, payment_type):
        journal = journal_id._get_available_payment_method_lines(payment_type)
        journal = journal.filtered(lambda a: a.code == 'manual')
        return journal

    def button_confirm(self):
        move_ids = self.env['account.move'].browse(
            self.env.context.get('active_ids'))
        for move in move_ids:
            if move.total_offset > move.amount_total:
                raise ValidationError(
                    _("""Waning! This process cannot continues because the amount to be processed is greater than the amount of this document"""))
            payment_type = 'inbound' if move.move_type == 'out_invoice' else 'outbound'
            partner_type = 'customer' if move.move_type == 'out_invoice' else 'supplier'
            journal_id = self._get_bank_journal()
            payment_method_line_id = self._get_manual_payment_method(
                journal_id, payment_type)
            move_payment_val = {
                'payment_type': payment_type,
                'partner_type': partner_type,
                'partner_id': move.partner_id.id,
                'amount': move.amount_total,
                'ref': 'Payment of ' + move.name,
                'journal_id': journal_id.id,
                'currency_id': move.currency_id.id,
                'payment_method_line_id': payment_method_line_id.id,
                'date': datetime.today(),
                'partner_bank_id': None,
                'destination_account_id': move.partner_id.property_account_receivable_id.id if partner_type == 'customer'
                else move.partner_id.property_account_payable_id.id
            }
            self.env['account.payment'].create(move_payment_val)
            # print('==================: 3 ', move.offset_ids)
            if move.offset_ids:
                # print('============================: 1')
                for offset in move.offset_ids:
                    invoice = offset.invoice_id
                    # print('====================: 2 ', invoice.name)
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
                        'payment_type': payment_type,
                        'partner_type': partner_type,
                        'partner_id': invoice.partner_id.id,
                        'amount': invoice.amount_total,
                        'ref': 'Payment of ' + invoice.name,
                        'journal_id': journal_id.id,
                        'currency_id': invoice.currency_id.id,
                        'payment_method_line_id': payment_method_line_id.id,
                        'date': datetime.today(),
                        'partner_bank_id': None,
                        'destination_account_id': invoice.partner_id.property_account_receivable_id.id if partner_type == 'customer'
                        else invoice.partner_id.property_account_payable_id.id
                    }
                    self.env['account.payment'].create(offset_payment_val)
