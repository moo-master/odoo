from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Tax Invoice Sequence",
        required=False,
        readonly=True,
    )
    credit_note_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Credit Note Sequence",
        required=False,
        readonly=True,
    )
    is_debit_note_sequence = fields.Boolean(
        string="Dedicated Debit Note Sequence",
    )
    debit_note_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Debit Note Sequence",
        required=False,
        readonly=True,
    )

    @api.onchange('type')
    def _onchange_type(self):
        self.refund_sequence = False

    def write(self, vals):
        for journal in self:
            credit_note, debit_note = self._get_prefix_refund()
            if journal.type in ['sale', 'purchase'] \
                    and journal.code and not journal.invoice_sequence_id:
                vals.update({
                    'invoice_sequence_id': journal._create_sequence(
                        journal.type, journal.code, 'invoice'
                    )
                })
            if journal.refund_sequence and not journal.credit_note_sequence_id:
                vals.update({
                    'credit_note_sequence_id': journal._create_sequence(
                        journal.type, credit_note, 'credit.note'
                    )
                })
            if journal.is_debit_note_sequence and not journal.debit_note_sequence_id:
                vals.update({
                    'debit_note_sequence_id': journal._create_sequence(
                        journal.type, debit_note, 'debit.note'
                    )
                })
        return super(AccountJournal, self).write(vals)

    def _create_sequence(self, journal_type, prefix, code):
        for journal in self:
            sequence = self.env['ir.sequence'].create(
                journal._prepare_data_date_ranges_sequence(
                    journal_type, prefix, code
                )
            )
            return sequence

    def _prepare_data_date_ranges_sequence(self, journal_type, prefix, code):
        vals = {
            'name': _('%s - %s') % (self.name, prefix),
            'code': '%s.%s' % (code, journal_type),
            'implementation': 'no_gap',
            'prefix': prefix + '%(range_y)s%(range_month)s-',
            'suffix': '',
            'padding': 5,
            'company_id': self.company_id.id,
            'use_date_range': True,
            'range': 'month',
        }
        return vals

    def _get_prefix_refund(self):
        credit_note = ''
        debit_note = ''
        if self.type == 'sale':
            credit_note = 'CN'
            debit_note = 'DN'
        elif self.type == 'purchase':
            credit_note = 'SCN'
            debit_note = 'SDN'
        return credit_note, debit_note
