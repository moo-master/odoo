from bahttext import bahttext
from datetime import timedelta, datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountBillingNote(models.Model):
    _name = 'account.billing.note'
    _description = 'Billing Note'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        domain="[('customer_rank', '>', 0),\
            ('company_id', 'in', [company_id, False])]",
        states={'draft': [('readonly', False)]},
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    name = fields.Char(
        string='Name',
    )

    bill_date = fields.Date(
        string='Billing Date',
        default=fields.Date.today(),
        required=True,
        states={'draft': [('readonly', False)]},
    )

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Credit Term',
        states={'draft': [('readonly', False)]},
    )

    payment_date = fields.Date(
        string='Payment Date',
        required=False,
        states={'draft': [('readonly', False)],
                'bill': [('readonly', False)]}
    )

    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('bill', 'Billing'),
            ('waiting_payment', 'Waiting Payment'),
            ('paid', 'Paid'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        tracking=True,
    )

    remark = fields.Text(
        string='Remark',
        states={'draft': [('readonly', False)]},
    )

    line_ids = fields.One2many(
        comodel_name='account.billing.note.line',
        inverse_name='billing_note_id',
        string='Account billing Note Line',
        copy=False,
        states={'draft': [('readonly', False)]},
    )

    receive_date = fields.Date(
        string='Receive Date',
    )

    invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice',
        related='line_ids.invoice_id',
        readonly=True,
        help="For search invoice line in billing note"
    )

    cancel_reason = fields.Char(
        string='Cancel Reason',
        readonly=True,
    )

    total_amount = fields.Float(
        string='Paid amount',
        compute='_compute_amount',
        store=True
    )

    wht_amount = fields.Float(
        string='WHT Amount',
        compute='_compute_amount',
        store=True
    )

    balance_amount = fields.Float(
        string='Balance Amount',
        compute='_compute_balance',
    )

    @staticmethod
    def _amount_total_text(amount):
        return bahttext(amount)

    @api.depends('line_ids')
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = sum(rec.line_ids.mapped('balance'))

    @api.depends('line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.wht_amount = sum(rec.line_ids.mapped('wht_total'))
            rec.total_amount = sum(rec.line_ids.mapped('paid_amount'))

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        self.payment_term_id = self.partner_id.property_payment_term_id.id

    @api.onchange("payment_term_id", "bill_date")
    def _onchange_payment_term_id(self):
        if self.payment_term_id.line_ids:
            if self.payment_term_id.name == 'End of Following Month':
                last_day = self.bill_date + relativedelta(months=1)
                self.payment_date = last_day.replace(
                    day=monthrange(last_day.year,
                                   last_day.month)[1])
            else:
                self.payment_date = self.bill_date + \
                    timedelta(days=self.payment_term_id.line_ids[0].days)

    def unlink(self):
        invoice_billing = self.filtered(lambda s: s.state == 'draft')
        return super(AccountBillingNote, invoice_billing).unlink()

    def button_customer_confirm(self):
        for rec in self:
            if not rec.receive_date:
                rec.write({
                    'receive_date': datetime.utcnow().date(),
                })
            rec.state = 'waiting_payment'

    def action_validate(self):
        if not self.line_ids:
            raise ValidationError(_(
                "Billing note must have at least one line to validate"
            ))

        seq_code = self.env.ref(
            'beecy_account_billing_note.sequence_account_billing_note').code
        seq_date = fields.Datetime.context_timestamp(
            self, fields.Datetime.to_datetime(self.bill_date)
        )
        self.name = self.env['ir.sequence'].next_by_code(
            seq_code, sequence_date=seq_date) or _('')
        self.state = 'bill'

    def action_print_billing_note(self):
        pass

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(self.env.context, state='cancel')
        return {
            'name': _('Cancel Billing Note'),
            'view_mode': 'form',
            'res_model': 'cancel.reject.reason',
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    def action_cancel_reason(self):
        for rec in self:
            for invoice in rec.line_ids.mapped('invoice_id'):
                bills = invoice.billing_note_ids.filtered(
                    lambda r: r.id == rec.id and invoice.id in r.invoice_id.ids
                )
                for bill in bills:
                    invoice.update({
                        'billing_note_ids': [(3, bill.id)],
                    })

    def action_filter(self):
        invoice_vals = self.prepare_invoice_filter()
        wizard = self.env['account.invoice.wizard'].create(invoice_vals)
        view_id = self.env.ref(
            'beecy_account_billing_note.account_invoice_wizard_views').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Choose Invoice'),
            'view_mode': 'tree',
            'res_model': 'account.invoice.wizard',
            'domain': [('id', 'in', wizard.ids)],
            'target': 'new',
            'views': [(view_id, 'tree')],
        }

    def action_showall(self):
        invoice_vals = self.prepare_invoice_all()
        self.update({'line_ids': invoice_vals})

    def action_paid(self):
        if self.line_ids:
            balance_check = self.line_ids.filtered(lambda r: r.balance > 0)
            if not balance_check:
                self.write({'state': 'paid'})

    def prepare_invoice_filter(self):
        return [
            {
                'invoice_id': invoice.id,
                'paid_amount': invoice.amount_residual,
                'billing_note_id': self.id,
            }
            for invoice in self._prepare_invoice()
            if not invoice.billing_note_ids
        ]

    def prepare_invoice_all(self):
        invoice_vals = []
        invoice_id = self._prepare_invoice()
        for invoice in invoice_id:
            if not invoice.billing_note_ids:
                balance = invoice.amount_residual
                amount = invoice.amount_total
                wht_total = invoice.amount_wht
                paid_amount = invoice.amount_residual
                if invoice.move_type == 'out_refund':
                    paid_amount = abs(paid_amount) * -1
                    amount = abs(amount) * -1
                    wht_total = abs(wht_total) * -1
                    balance = abs(balance) * -1
                val = (0, 0, {
                    'invoice_id': invoice.id,
                    'billing_note_id': self.id,
                    'paid_amount': paid_amount,
                    'wht_total': wht_total,
                    'amount': amount,
                    'balance': balance,
                })
                invoice_vals.append(val)
        return invoice_vals

    def _prepare_invoice(self):
        invoice_obj = self.env['account.move']
        all_bills = self.search([('state', '!=', 'cancel')])
        all_bills |= self
        invoice_ids = all_bills.mapped('line_ids').filtered(
            lambda x: x.is_billing).mapped('invoice_id').ids
        invoice_id = invoice_obj.search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', 'in', ('out_invoice', 'out_refund', 'out_debit')),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('id', 'not in', invoice_ids)
        ])
        return invoice_id
