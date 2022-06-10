from odoo import models, fields, api


class BeecyAccountPayment(models.Model):
    _inherit = 'beecy.account.payment'

    temp_journal_ids = fields.One2many(
        comodel_name='temp.journal.item',
        inverse_name='payment_id',
        string='Journal Items',
    )

    move_line_ids = fields.One2many(
        comodel_name='account.move.line',
        string='Move Line',
        related='relate_move_id.line_ids',
    )

    @api.onchange('payment_line_invoice_ids',
                  'payment_line_method_ids', 'amount_wht')
    def _onchange_create_temp_journal_item(self):
        journal_ids = []
        remove_temp_line = self.temp_journal_ids.mapped(
            lambda v: (2, v.id)
        )

        if self.payment_type == 'inbound':
            for rec in self.payment_line_invoice_ids:
                journal_ids.append((0, 0, {
                    'account_id': self.partner_id.property_account_receivable_id.id or False,
                    'name': rec.invoice_id.name,
                    'debit': 0,
                    'credit': rec.amount_tobe_paid,
                    'invoice_id': rec.invoice_id.id or False,
                }))
                if rec.invoice_id.tax_id.tax_exigibility == 'on_payment':
                    journal_ids.append((0, 0, {
                        'account_id': rec.invoice_id.tax_id.cash_basis_transition_account_id.id or False,
                        'name': rec.invoice_id.name,
                        'debit': rec.invoice_id.amount_tax,
                        'credit': 0,
                    }))
                    journal_ids.append((0, 0, {
                        'account_id': rec.invoice_id.tax_id.invoice_repartition_line_ids.account_id.id or False,
                        'name': rec.invoice_id.name,
                        'debit': 0,
                        'credit': rec.invoice_id.amount_tax,
                    }))

            if self.amount_wht:
                journal_ids.append(
                    (0, 0, {
                        'account_id': self.company_id.ar_wht_default_account_id.id or False,
                        'name': "ภาษีหัก ณ ที่จ่าย",
                        'debit': self.amount_wht,
                        'credit': 0,
                        'is_wht': True,
                    })
                )

            for met_line in self.payment_line_method_ids:
                inbound_acc_ids = met_line.payment_method_line_id.journal_id.mapped(
                    'inbound_payment_method_line_ids')
                for inbound_line in inbound_acc_ids:
                    if met_line.payment_method_line_id.name == inbound_line.name:
                        journal_ids.append(
                            (0, 0, {
                                'account_id': inbound_line.payment_account_id.id or False,
                                'name': inbound_line.name,
                                'debit': met_line.amount_total,
                                'credit': 0,
                            })
                        )
        else:
            for rec in self.payment_line_invoice_ids:
                journal_ids.append((0, 0, {
                    'account_id': self.partner_id.property_account_payable_id.id or False,
                    'name': rec.invoice_id.name,
                    'debit': rec.amount_tobe_paid,
                    'credit': 0,
                    'invoice_id': rec.invoice_id.id or False,
                }))
                if rec.invoice_id.tax_id.tax_exigibility == 'on_payment':
                    journal_ids.append((0, 0, {
                        'account_id': rec.invoice_id.tax_id.cash_basis_transition_account_id.id or False,
                        'name': rec.invoice_id.name,
                        'debit': 0,
                        'credit': rec.invoice_id.amount_tax,
                    }))
                    journal_ids.append((0, 0, {
                        'account_id': rec.invoice_id.tax_id.invoice_repartition_line_ids.account_id.id or False,
                        'name': rec.invoice_id.name,
                        'debit': rec.invoice_id.amount_tax,
                        'credit': 0,
                    }))

            if self.amount_wht:
                journal_ids.append(
                    (0, 0, {
                        'account_id': self.company_id.ap_wht_default_account_id.id or False,
                        'name': "ภาษีหัก ณ ที่จ่าย",
                        'debit': 0,
                        'credit': self.amount_wht,
                        'is_wht': True,
                    })
                )

            for met_line in self.payment_line_method_ids:
                outbound_acc_ids = met_line.payment_method_line_id.journal_id.mapped(
                    'outbound_payment_method_line_ids')
                for outbound_line in outbound_acc_ids:
                    if met_line.payment_method_line_id.name == outbound_line.name:
                        journal_ids.append(
                            (0, 0, {
                                'account_id': outbound_line.payment_account_id.id or False,
                                'name': outbound_line.name,
                                'debit': 0,
                                'credit': met_line.amount_total,
                            })
                        )

        self.write({'temp_journal_ids': journal_ids + remove_temp_line})

    def action_to_paid(self):
        super().action_to_paid()
        self.create_account_move_entry()

    # overwrite
    def create_account_move_entry(self):
        move = {
            'name': '/',
            'journal_id': self.journal_id.id,
            'date': self.date_date,
            'beecy_payment_id': self.id,
            'move_type': 'entry',
            'currency_id': self.currency_id.id,
            'ref': self.name
        }
        move_id = self.env['account.move'].create(move)
        line_invoice_ids = []
        for rec in self.temp_journal_ids:
            line_invoice_ids.append((0, 0, {
                'account_id': rec.account_id.id,
                'partner_id': self.partner_id.id,
                'name': rec.name,
                'debit': rec.debit,
                'credit': rec.credit,
            }))
        move_id.write({
            'line_ids': line_invoice_ids
        })
        move_id.action_post()
        return self.write({'state': 'paid', 'relate_move_id': move_id})
