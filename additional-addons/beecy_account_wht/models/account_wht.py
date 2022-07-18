from odoo import fields, models, api, _
import re
from bahttext import bahttext


class AccountWht(models.Model):
    _name = 'account.wht'
    _description = 'Account WHT'

    @api.depends('line_ids', 'base_amount')
    def _compute_tax(self):
        result = {}
        for rec in self:
            result[rec] = {
                'tax': 0.0,
                'base_amount': 0.0,
            }
            data = self.browse([rec])[0]
            val = val1 = 0.0
            for line in data.id.line_ids:
                val1 += line.base_amount
                val += line.tax
            rec.tax = val
            rec.base_amount = val1

    name = fields.Char(
        'No.',
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',)
    document_date = fields.Date(
        'Document Date',
        required=True,)
    wht_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')
    ],
        string='Type of WHT',
        required=True,)
    wht_kind = fields.Selection([
        ('pnd1k', '(1) P.N.D.1 K'),
        ('pnd1ks', '(2) P.N.D.1 K Special'),
        ('pnd2', '(3) P.N.D.2'),
        ('pnd3', '(4) P.N.D.3'),
        ('pnd2k', '(5) P.N.D.2 K'),
        ('pnd3k', '(6) P.N.D.3 K'),
        ('pnd53', '(7) P.N.D.53')
    ],
        string='Kind of WHT',
        required=True,)
    wht_payment = fields.Selection([
        ('wht', '(1) With holding tax'),
        ('forever', '(2) Forever'),
        ('once', '(3) Once'),
        ('other', '(4) Other')
    ],
        string='WHT Payment',
        default='wht',
        required=True,)
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,)
    base_amount = fields.Float(
        'Base Amount',
        compute='_compute_base_amount',)
    wht_amount = fields.Float(
        'WHT Amount',
        compute='_compute_wht_amount',)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ],
        copy=False,
        default='draft',
        string='Status',)
    note = fields.Html(
        'Note',)
    line_ids = fields.One2many(
        'account.wht.line',
        'wht_id',)
    tax = fields.Float(
        compute='_compute_tax',
        digits='Account',
        string='Tax'
    )

    invoice_line_ids = fields.Many2many(
        'account.move.line',
        compute='_compute_invoice_line_ids',
        string='Invoice IDS',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.line_ids = False
        if self.partner_id.company_type == 'person':
            self.wht_kind = 'pnd3'
        elif self.partner_id.company_type == 'company':
            self.wht_kind = 'pnd53'

    @api.depends('line_ids')
    def _compute_invoice_line_ids(self):
        for rec in self:
            Account_move = self.env['account.move']
            list_invoice_line_ids = []
            if rec.wht_type == 'sale':
                list_invoice_line_ids = Account_move.search(
                    [('move_type', 'in',
                        ('in_invoice', 'in_refund', 'in_receipt', 'in_debit'))
                     ]).mapped('invoice_line_ids').ids
            else:
                list_invoice_line_ids = Account_move.search(
                    [('move_type', 'in',
                        ('out_invoice', 'out_refund', 'out_receipt', 'out_debit'))
                     ]).mapped('invoice_line_ids').ids
            rec.invoice_line_ids = rec.line_ids.mapped(
                'invoice_line_id').ids + list_invoice_line_ids

    @api.depends('line_ids')
    def _compute_base_amount(self):
        for rec in self:
            rec.base_amount = sum(rec.line_ids.mapped('base_amount'))

    @api.depends('line_ids')
    def _compute_wht_amount(self):
        for rec in self:
            rec.wht_amount = sum(rec.line_ids.mapped('wht_amount'))

    def action_set_to_draft(self):
        self.update({
            'status': 'draft'
        })

    def action_done(self):
        for rec in self:
            if not rec.name:
                code = 'seq.account.wht.vendor'
                if rec.wht_type == 'sale':
                    code = 'seq.account.wht.customer'
                rec.name = rec.env['ir.sequence'].next_by_code(
                    code, sequence_date=rec.document_date) or _('')
            rec.write({
                'status': 'done',
            })
        return True

    def split_id_card(self):
        if self.partner_id.vat and len(self.partner_id.vat) == 13:
            card_1 = self.partner_id.vat[0]
            card_2 = self.partner_id.vat[1:5]
            card_3 = self.partner_id.vat[5:10]
            card_4 = self.partner_id.vat[10:12]
            card_5 = self.partner_id.vat[12]
            return card_1, card_2, card_3, card_4, card_5
        return False

    def split_company_id_card(self):
        company = self.env.company
        if company.vat and len(company.vat) == 13:
            card_1 = company.vat[0]
            card_2 = company.vat[1:5]
            card_3 = company.vat[5:10]
            card_4 = company.vat[10:12]
            card_5 = company.vat[12]
            return card_1, card_2, card_3, card_4, card_5
        return False

    def split_datetime(self, move_date=None):
        if move_date:
            date = move_date
        else:
            date = self.document_date
        days = str(date).split('-')[2]
        month = str(date).split('-')[1]
        year = int(str(date).split('-')[0]) + 543
        if move_date:
            return f"{days}/{month}/{year}"
        return [days, month, year]

    def prepare_lines_wht(self):
        if not self.line_ids:
            return {}
        lines_wht = self._create_lines_wht()
        for line in self.line_ids:
            wht = line.wht_type_id.name
            if wht:
                wht_1 = re.search(r'40\s\S+(1)\S+', wht)
                wht_2 = re.search(r'40\s\S+(2)\S+', wht)
                wht_3 = re.search(r'40\s\S+(3)\S+', wht)
                wht_4 = re.search(r'40\s\S+(4)\S+(ก)\S+', wht)
                # wht 4.1
                wht_4_1 = re.search(r'40\s\S+(4)\S+(ข)\S+', wht)
                wht_4_1_1 = re.search(r'4\s\S+(1.1)\S+', wht)
                wht_4_1_2 = re.search(r'4\s\S+(1.2)\S+', wht)
                wht_4_1_3 = re.search(r'4\s\S+(1.3)\S+', wht)
                wht_4_1_4 = re.search(r'4\s\S+(1.4)\S+', wht)
                # wht 4.2
                wht_4_2_1 = re.search(r'4\s\S+(2.1)\S+', wht)
                wht_4_2_2 = re.search(r'4\s\S+(2.2)\S+', wht)
                wht_4_2_3 = re.search(r'4\s\S+(2.3)\S+', wht)
                wht_4_2_4 = re.search(r'4\s\S+(2.4)\S+', wht)
                wht_4_2_5 = re.search(r'4\s\S+(2.5)\S+', wht)
                # wht 5
                wht_5 = re.search(r'5 การจ่ายเงินได้ที่ต้องหักภาษี', wht)
                wht_5_1 = re.search(r'5.1', wht)
                wht_5_2 = re.search(r'5.2', wht)
                wht_5_3 = re.search(r'5.3', wht)
                wht_5_4 = re.search(r'5.4', wht)
                wht_5_5 = re.search(r'5.5', wht)
                list_wht_5 = [
                    wht_5,
                    wht_5_1,
                    wht_5_2,
                    wht_5_3,
                    wht_5_4,
                    wht_5_5]
                # wht 6
                wht_6 = re.search(r'6 อื่นๆ', wht)
                wht_6_1 = re.search(r'6.1', wht)
                wht_6_2 = re.search(r'6.2', wht)
                wht_6_3 = re.search(r'6.3', wht)
                wht_6_4 = re.search(r'6.4', wht)
                wht_6_5 = re.search(r'6.5', wht)
                wht_6_6 = re.search(r'6.6', wht)
                list_wht_6 = [
                    wht_6,
                    wht_6_1,
                    wht_6_2,
                    wht_6_3,
                    wht_6_4,
                    wht_6_5,
                    wht_6_6]
                # group line wht
                self.update_line_wht(
                    lines_wht,
                    line,
                    wht_1,
                    wht_2,
                    wht_3,
                    wht_4,
                    wht_4_1,
                    wht_4_1_1,
                    wht_4_1_2,
                    wht_4_1_3,
                    wht_4_1_4,
                    wht_4_2_1,
                    wht_4_2_2,
                    wht_4_2_3,
                    wht_4_2_4,
                    wht_4_2_5,
                    list_wht_5,
                    list_wht_6)
        lines_wht.update({
            'wht_note_4_2_5': ", ".join(lines_wht['list_wht_note_4_2_5']),
            'wht_note_6': ", ".join(lines_wht['list_wht_note_6'])
        })
        return lines_wht

    def _create_lines_wht(self):
        list_wht = [
            'wht_1',
            'wht_2',
            'wht_3',
            'wht_4',
            'wht_4_1_1',
            'wht_4_1_2',
            'wht_4_1_3',
            'wht_4_1_4',
            'wht_4_2_1',
            'wht_4_2_2',
            'wht_4_2_3',
            'wht_4_2_4',
            'wht_4_2_5',
            'wht_5',
            'wht_6',
        ]
        lines_wht = {}
        for wht in list_wht:
            lines_wht.update({
                f'seq_{wht}_date': '',
                # total_base_amount
                'wht_total_base_amount': 0,
                f'seq_{wht}_total_base_amount': 0,
                f'seq_{wht}_base_amount': 0,
                f'seq_{wht}_base_amount_precision': 0,
                'total_base_amount': 0,
                'wht_total_base_amount_precision': 0,
                # total_tax_amount
                f'seq_{wht}_total_tax_amount': 0,
                f'seq_{wht}_tax_amount': 0,
                f'seq_{wht}_tax_amount_precision': 0,
                'wht_note_4_2_5': '',
                'list_wht_note_4_2_5': [],
                'wht_note_6': '',
                'list_wht_note_6': [],
                'wht_total_tax_amount': 0,
                'th_wht_total_tax_amount': '',
                'total_tax_amount': 0,
                'wht_total_tax_amount_precision': 0,
            })
        return lines_wht

    def update_line_wht(
            self,
            lines_wht,
            line,
            wht_1,
            wht_2,
            wht_3,
            wht_4,
            wht_4_1,
            wht_4_1_1,
            wht_4_1_2,
            wht_4_1_3,
            wht_4_1_4,
            wht_4_2_1,
            wht_4_2_2,
            wht_4_2_3,
            wht_4_2_4,
            wht_4_2_5,
            list_wht_5,
            list_wht_6,):
        if wht_1 and wht_1.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_1',
            )
        elif wht_2 and wht_2.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_2',
            )
        elif wht_3 and wht_3.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_3',
            )
        elif wht_4 and wht_4.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4',
            )
        elif wht_4_1_1 and wht_4_1 and all([wht_4_1_1.group(), wht_4_1.group()]):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_1_1',
            )
        elif wht_4_1_2 and wht_4_1 and all([wht_4_1_2.group(), wht_4_1.group()]):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_1_2',
            )
        elif wht_4_1_3 and wht_4_1 and all([wht_4_1_3.group(), wht_4_1.group()]):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_1_3',
            )
        elif wht_4_1_4 and wht_4_1 and all([wht_4_1_4.group(), wht_4_1.group()]):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_1_4',
            )
        elif wht_4_2_1 and wht_4_2_1.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_2_1',
            )
        elif wht_4_2_2 and wht_4_2_2.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_2_2',
            )
        elif wht_4_2_3 and wht_4_2_3.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_2_3',
            )
        elif wht_4_2_4 and wht_4_2_4.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_2_4',
            )
        elif wht_4_2_5 and wht_4_2_5.group():
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_4_2_5',
            )
        elif any(list_wht_5):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_5',
            )
        elif any(list_wht_6):
            self.update_group_data_line_wht(
                lines_wht,
                line,
                'wht_6',
            )

    def update_group_data_line_wht(
            self,
            lines_wht,
            line,
            seq_wht):
        # sum amount total by groups
        seq_base_amount = f'seq_{seq_wht}_total_base_amount'
        seq_tax_amount = f'seq_{seq_wht}_total_tax_amount'
        # all sum amount total
        sum_total_amount = lines_wht['total_base_amount'] + line.base_amount
        sum_total_tax_amount = lines_wht['total_tax_amount'] + line.tax
        lines_wht.update({
            seq_base_amount: lines_wht[seq_base_amount] + line.base_amount,
            seq_tax_amount: lines_wht[seq_tax_amount] + line.tax,
            'total_base_amount': sum_total_amount,
            'total_tax_amount': sum_total_tax_amount
        })
        # note wht 6, 4.2.5
        if line.note:
            if seq_wht == 'wht_4_2_5':
                lines_wht['list_wht_note_4_2_5'].append(line.note)
            elif seq_wht == 'wht_6':
                lines_wht['list_wht_note_6'].append(line.note)
        # base_amount
        amount = "{0:.2f}".format(
            round(lines_wht[seq_base_amount], 2))
        base_amount = amount.split('.')[0]
        base_amount_precision = amount.split('.')[1]
        # tax_amount
        tax = "{0:.2f}".format(
            round(lines_wht[seq_tax_amount], 2))
        tax_amount = tax.split('.')[0]
        tax_amount_precision = tax.split('.')[1]
        # Split update total_base_amount, wht_total_base_amount_precision
        total_base_amount = "{0:.2f}".format(
            round(lines_wht['total_base_amount'], 2))
        total_amount = total_base_amount.split('.')[0]
        total_amount_precision = total_base_amount.split('.')[1]
        # Split update total_tax_amount, wht_total_tax_amount_precision
        total_tax_amount = "{0:.2f}".format(
            round(lines_wht['total_tax_amount'], 2))
        total_tax = total_tax_amount.split('.')[0]
        total_tax_amount_precision = total_tax_amount.split('.')[1]
        # update amount
        lines_wht.update({
            f'seq_{seq_wht}_base_amount': "{:,}".format(int(base_amount)),
            f'seq_{seq_wht}_base_amount_precision': base_amount_precision,
            f'seq_{seq_wht}_date': self.split_datetime(line.invoice_line_id.date),
            f'seq_{seq_wht}_tax_amount': "{:,}".format(int(tax_amount)),
            f'seq_{seq_wht}_tax_amount_precision': tax_amount_precision,
            'wht_total_base_amount': "{:,}".format(int(total_amount)),
            'wht_total_base_amount_precision': total_amount_precision,
            'wht_total_tax_amount': "{:,}".format(int(total_tax)),
            'wht_total_tax_amount_precision': total_tax_amount_precision,
            'th_wht_total_tax_amount': self._amount_total_text(
                lines_wht['total_tax_amount'])
        })

    def _amount_total_text(self, amount):
        return bahttext(amount)
