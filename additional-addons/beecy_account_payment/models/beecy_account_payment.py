from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from bahttext import bahttext


class BeecyAccountPayment(models.Model):
    _name = 'beecy.account.payment'
    _description = 'Beecy Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    name = fields.Char(
        string='Number',
    )
    relate_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        domain="[('company_id', 'in', [company_id, False])]",
        states={'draft': [('readonly', False)]},
    )
    payment_type = fields.Selection(
        selection=[
            ('outbound', 'Vendor'),
            ('inbound', 'Customer'),
        ],
        string='Payment Type',
        default='inbound',
        required=True,
        tracking=True,
    )
    date_date = fields.Date(
        string='Payment Date',
        default=fields.Date.today,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string='Note',
        states={'draft': [('readonly', False)]},
    )
    vat_date = fields.Date(
        string='Vat Date',
        states={'draft': [('readonly', False)]}
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('waiting_payment', 'Waiting Payment'),
            ('paid', 'Paid'),
            ('reject', 'Reject'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        tracking=True,
    )
    amount_balance = fields.Monetary(
        string='Amount Balance',
        compute='_compute_amount_all',
    )
    amount_tobe_paid = fields.Monetary(
        string='Amount To be Paid',
        compute='_compute_amount_all',
    )
    amount_wht = fields.Monetary(
        string='Amount WHT',
        compute='_compute_amount_all',
    )
    amount_paid = fields.Monetary(
        string='Paid Amount',
        compute='_compute_amount_all',
    )

    cancel_reason = fields.Char(
        string='Cancel Reason',
        readonly=True,
    )

    reject_reason = fields.Char(
        string='Reject Reason Note',
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda x: x.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda x: x.env.company.currency_id,
    )
    payment_line_invoice_ids = fields.One2many(
        comodel_name='account.payment.line.invoice',
        inverse_name='payment_id',
        string='Account Payment Line Invoice',
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    payment_line_wht_ids = fields.One2many(
        comodel_name='account.payment.line.wht',
        inverse_name='payment_id',
        string='Account Payment Line WHT',
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    payment_line_method_ids = fields.One2many(
        comodel_name='account.payment.line.method',
        inverse_name='payment_id',
        string='Account Payment Line Method',
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    wht_payment = fields.Selection([
        ('wht', '(1) With holding tax'),
        ('forever', '(2) Forever'),
        ('once', '(3) Once'),
        ('other', '(4) Other')
    ], 'Withholding Tax',
        default='wht',
        required=True,
    )

    left_paid_amount = fields.Float(
        compute='_compute_amount_all',
    )

    billing_note_id = fields.Many2one(
        comodel_name='account.billing.note',
        string='Billing Note',
        copy=False,
        index=True,
        ondelete='cascade',
    )
    is_check_line_invoice = fields.Boolean(
        string='Payment Invoice Line',
    )

    @api.depends('payment_line_invoice_ids',
                 'payment_line_method_ids',
                 'payment_line_wht_ids')
    def _compute_amount_all(self):
        for rec in self:
            rec.amount_balance = sum(
                rec.payment_line_invoice_ids.mapped('amount_residual')) or 0.0
            rec.amount_tobe_paid = sum(
                rec.payment_line_invoice_ids.mapped('amount_tobe_paid')) or 0.0
            rec.amount_wht = sum(map(rec.currency_id.round,
                                     rec.payment_line_wht_ids.mapped('amount_wht'))) or 0.0
            rec.amount_paid = sum(rec.payment_line_method_ids.mapped(
                'amount_total')) or 0.0
            rec.left_paid_amount = rec.amount_tobe_paid\
                - rec.amount_wht - rec.amount_paid
            rec.check_count_line_invoice()

    def action_confirm(self):
        section_5_list = []
        section_6_list = []
        for line in self.payment_line_wht_ids:
            if (line.wht_type_id.sequence in [
                    5, 500] and line.wht_type_id.id not in section_5_list):
                section_5_list.append(line.wht_type_id.id)
            if (line.wht_type_id.sequence in [
                    6, 600] and line.wht_type_id.id not in section_6_list):
                section_6_list.append(line.wht_type_id.id)
        if 1 < len(section_5_list) or 1 < len(section_6_list):
            raise ValidationError(
                _("You can not select different WHT under the same category."
                  " Right now your section 5 or section 6"
                  " are under the same category."))
        vendor_steps = self.company_id.beecy_account_payment_vendor_steps
        if self.payment_type == 'outbound':
            code = 'payment.outbornd.beecy'
            self.name = self.create_sequence_id(code)
            if vendor_steps == 'two_step':
                self.action_to_approve()
            else:
                self.action_waiting_payment()
        else:
            code = 'payment.inbornd.beecy'
            self.name = self.create_sequence_id(code)
            self.action_waiting_payment()

    def create_sequence_id(self, code):
        return self.env['ir.sequence'].next_by_code(
            code, sequence_date=self.date_date)

    def action_to_approve(self):
        self.write({
            'state': 'to_approve'
        })

    def action_waiting_payment(self):
        self.write({
            'state': 'waiting_payment'
        })

    def action_to_paid(self):
        for rec in self.payment_line_invoice_ids.mapped('invoice_id'):
            rec.write({
                'beecy_payment_id': self.id,
            })
        self.write({
            'state': 'paid'
        })

    def action_set_to_draft(self):
        self.write({
            'state': 'draft'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    def action_reject(self):
        self.write({
            'state': 'reject'
        })

    def action_validate(self):
        vendor_steps = self.company_id.beecy_account_payment_vendor_steps
        if self.payment_type == 'outbound':
            if vendor_steps == 'two_step':
                self.action_to_approve()
            else:
                self.action_waiting_payment()
        else:
            self.action_waiting_payment()
        amount_inv = sum(
            self.payment_line_invoice_ids.mapped('amount_tobe_paid')
        )
        amount_wht = sum(
            self.payment_line_wht_ids.mapped('amount_wht')
        )
        amount_method = sum(
            self.payment_line_method_ids.mapped('amount_total')
        )

        if round(amount_inv, 2) - (round(amount_wht, 2)
                                   + round(amount_method, 2)) > 0:

            raise ValidationError(
                _("The amount to be paid doesn't "
                  "equal to the paid amount + amount WHT.!"))

        vendor_steps = self.company_id.beecy_account_payment_vendor_steps
        if self.payment_type == 'outbound':
            if vendor_steps == 'two_step':
                self.action_to_approve()
            else:
                self.action_to_paid()
        else:
            self.action_to_paid()

    def action_approve(self):
        pass

    def action_account_wht_print(self):
        pass

    @api.onchange('payment_line_invoice_ids')
    def _onchange_payment_line_invoice_ids(self):
        move_ids = []
        if self.payment_line_invoice_ids:
            move_ids = self.payment_line_invoice_ids.mapped('invoice_id').ids
        move_line = self.env['account.move.line'].search([
            ('move_id', 'in', move_ids),
            ('wht_type_id', '!=', False)
        ])
        val_wht = []
        for rec in move_line:
            val_wht.append((0, 0, {
                'invoice_line_id': rec.id,
                'wht_type_id': rec.wht_type_id.id,
                'percent': rec.wht_type_id.percent,
                'amount_wht': rec.amount_wht,
            }))
        remove_wht_line = self.payment_line_wht_ids.mapped(
            lambda v: (2, v.id)
        )
        self.write({
            'payment_line_wht_ids': remove_wht_line + val_wht
        })
        self.check_count_line_invoice()

    def get_account_move(self, domain, choose):
        if choose == 'bill_note':
            account_move_data = self.env['account.billing.note'].search(domain)
        else:
            account_move_data = self.env['account.move'].search(domain)

        payment_line = self.env['account.payment.line.invoice']
        val_data = []

        if choose == 'bill_note':
            for line in account_move_data:
                payment_ids = payment_line.search([
                    ('invoice_id', 'in', line.line_ids.mapped('invoice_id').ids)
                ])
                invoice_ids = payment_ids.mapped('invoice_id')
                account_move = line.line_ids.mapped('invoice_id').ids
                for r in invoice_ids.ids:
                    indexes = [i for i, x in enumerate(account_move) if x == r]
                    if indexes and len(indexes) == 1:
                        account_move.pop(indexes[0])
                for rec in line.line_ids.filtered(
                        lambda l: not l.invoice_id.id not in account_move):
                    billing_id = rec.billing_note_id
                    rec = rec.invoice_id
                    val_data.append(
                        {'move_id': rec.id,
                         'company_id': rec.company_id.id,
                         'currency_id': rec.currency_id.id,
                         'name': billing_id.name,
                         'partner_id': rec.partner_id.id,
                         'invoice_partner_display_name':
                             rec.invoice_partner_display_name,
                         'invoice_date': rec.invoice_date,
                         'invoice_due_date': rec.invoice_date_due,
                         'amount_untaxed_signed': rec.amount_untaxed_signed,
                         'amount_total_signed': rec.amount_total_signed,
                         'state': rec.state,
                         'move_type': rec.move_type})

        else:
            payment_ids = payment_line.search([
                ('invoice_id', '=', account_move_data.ids)
            ])
            invoice_ids = payment_ids.mapped('invoice_id').ids
            account_move = account_move_data.ids
            for r in invoice_ids:
                indexes = [i for i, x in enumerate(account_move) if x == r]
                if indexes and len(indexes) == 1:
                    account_move.pop(indexes[0])
            for rec in account_move_data.browse(account_move):
                val_data.append(
                    {'move_id': rec.id,
                     'company_id': rec.company_id.id,
                     'currency_id': rec.currency_id.id,
                     'name': rec.name,
                     'partner_id': rec.partner_id.id,
                     'invoice_partner_display_name':
                         rec.invoice_partner_display_name,
                     'invoice_date': rec.invoice_date,
                     'invoice_due_date': rec.invoice_date_due,
                     'amount_untaxed_signed': rec.amount_untaxed_signed,
                     'amount_total_signed': rec.amount_total_signed,
                     'state': rec.state,
                     'move_type': rec.move_type}
                )
        return val_data

    def action_get_account_move(self):
        ctx = dict(self.env.context)
        # Note: Customer: CN: move_type = 'out_refund' DN: move_type = 'out_debit'
        # Vendor: CN: move_type = 'in_refund' DN: move_type = 'in_debit'
        if 'choose' in ctx:
            if ctx.get('choose') in ['manual', 'auto']:
                domain = [
                    ('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'paid'),
                    ('move_type', 'in', ctx.get('move_type')),
                    ('amount_residual', '>', 0),
                    ('billing_note_ids', '=', False)
                ]
            else:
                domain = [
                    ('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'waiting_payment'),
                    ('invoice_id.billing_note_ids', '=', False)
                ]
            val_data = self.get_account_move(domain, ctx.get('choose'))
            wizard = self.env['payment.account.move.wizard'].create(val_data)
            view_id = self.env.ref(
                'beecy_account_payment.payment_account_move_wizard_views')

            if ctx.get('choose') == 'auto':
                invoice = []
                for line in wizard:
                    val = (0,
                           0,
                           {'invoice_id': line.move_id.id,
                            'invoice_date_due_date': line.invoice_due_date,
                            'amount_untaxed': line.move_id.amount_untaxed,
                            'amount_total': line.move_id.amount_total,
                            'currency_id': line.currency_id,
                            'amount_wht': line.move_id.amount_wht,
                            'amount_residual': line.move_id.amount_residual,
                            'amount_tobe_paid': line.move_id.amount_residual,
                            })
                    invoice.append(val)
                remove_invoice_line = self.payment_line_invoice_ids.mapped(
                    lambda v: (2, v.id))
                self.update(
                    {'payment_line_invoice_ids': invoice + remove_invoice_line})
                self._onchange_payment_line_invoice_ids()
                account_move_data = self.env['account.move'].search(domain)
                for acc_line in account_move_data:
                    acc_line.beecy_payment_id = self.id

                return True
            return {
                'type': 'ir.actions.act_window',
                'name': _('Choose Invoice'),
                'view_mode': 'tree',
                'res_model': 'payment.account.move.wizard',
                'context': {'default_move_type': 'out_invoice',
                            'payment_id': self.id},
                'domain': [('id', 'in', wizard.ids)],
                'target': 'new',
                'views': [(view_id.id, 'tree')],
            }

    def create_account_move_entry(self):
        move = {
            'name': '/',
            'journal_id': self.journal_id.id,
            'date': self.date_date,
            'beecy_payment_id': self.id,
            'move_type': 'entry',
        }

        move_id = self.env['account.move'].create(move)
        line_invoice_ids = []

        for rec in self.payment_line_invoice_ids:
            account_id = self.partner_id.property_account_receivable_id
            account_payable = self.partner_id.property_account_payable_id
            val_debit = (0, 0, {
                'partner_id': self.partner_id.id,
                'debit': rec.amount_tobe_paid - rec.amount_wht,
                'account_id': account_id.id,
            })

            val_credit = (0, 0, {
                'partner_id': self.partner_id.id,
                'credit': rec.amount_tobe_paid,
                'account_id': rec.invoice_id.journal_id.default_account_id.id,
            })
            if rec.amount_wht:
                val_wht = (0, 0, {
                    'partner_id': self.partner_id.id,
                    'debit': rec.amount_wht,
                    'account_id': account_payable.id,
                })
                line_invoice_ids.append(val_wht)
            line_invoice_ids.append(val_debit)
            line_invoice_ids.append(val_credit)
        move_id.write({
            'line_ids': line_invoice_ids
        })
        move_id.action_post()
        return self.write({'state': 'paid', 'relate_move_id': move_id})

    def action_cancel_reject_reason_wizard(self):
        ctx = dict(self.env.context)
        ctx.update({
            'active_model': 'beecy.account.payment',
            'active_id': self.id,
        })
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        return {
            'name': _('Cancel Account Payment'),
            'view_mode': 'form',
            'res_model': 'cancel.reject.reason',
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'target': 'new'
        }

    def _amount_total_text(self, amount):
        return bahttext(amount)

    def prepare_lines_payment_method(self):
        method_name = []
        for method_payment in self.payment_line_method_ids.mapped(
                'payment_method_line_id'):
            method_name.append(method_payment.name)
        method_name.append("ภาษีถูกหัก ณ ที่จ่าย")
        method_name.append("ส่วนลด")
        method_name.append("รวมมูลค่าที่ชำระ / Total Payment")
        return method_name

    def prepare_amount_payment_method(self):
        method_amount = []
        for method_payment in self.payment_line_method_ids.mapped(
                'payment_method_line_id'):
            amount_method = sum(self.payment_line_method_ids.filtered(
                lambda m: m.payment_method_line_id.id
                == method_payment.id).mapped('amount_total'))
            method_amount.append("{:,.2f}".format(amount_method))
        amount_total = sum(
            self.payment_line_method_ids.mapped('amount_total'))
        method_amount.append("{:,.2f}".format(self.amount_wht))
        method_amount.append('-')
        method_amount.append("{:,.2f}".format(amount_total))
        return method_amount

    def check_count_line_invoice(self):
        for rec in self:
            num_invoice = len(rec.payment_line_invoice_ids)
            if num_invoice > 1:
                rec.is_check_line_invoice = True
            else:
                rec.is_check_line_invoice = False

    @api.model
    def fields_view_get(self,
                        view_id=None,
                        view_type='tree',
                        toolbar=False,
                        submenu=False
                        ):
        res = super(BeecyAccountPayment, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        if toolbar:
            context = dict(self._context or {})
            payment_type = context.get('default_payment_type', [])
            data_report = self.prepare_data_report(payment_type)
            if data_report:
                for report_id in data_report:
                    for report in res['toolbar']['print']:
                        if report_id == report['id']:
                            res['toolbar']['print'].remove(report)

        return res

    def prepare_data_report(self, payment_type):
        data_report = []
        if payment_type == 'inbound':
            report_templte = [
                'beecy_account_payment.action_payment_voucher_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)

        if payment_type == 'outbound':
            report_templte = [
                'beecy_account_payment.action_payment_receipt_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)
        return data_report

    def prepare_action_menu_report(self, report_templte):
        data_report = []
        for rec in report_templte:
            data_report.append(self.env.ref(rec).id)
        return data_report
