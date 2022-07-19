from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class AccountCheque(models.Model):
    _name = 'account.cheque'
    _description = 'Account Cheque'
    _rec_name = "name"

    def _default_get_journal(self):
        cheque_type = self._context.get('default_type', False)
        if cheque_type == 'vendor':
            return self.env.company.default_vendor_cheque_journal_id.id
        elif cheque_type == 'customer':
            return self.env.company.default_customer_cheque_journal_id.id

    name = fields.Char(
        string='Cheque No.',
        states={'close': [('readonly', True)]},
    )

    type = fields.Selection(
        string='Type',
        selection=[
            ('vendor', 'Vendor'),
            ('customer', 'Customer'),
        ],
        readonly=True,
    )

    cheque_date = fields.Date(
        string='Cheque Date',
        states={'close': [('readonly', True)]},
    )

    from_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='From Bank',
        states={'close': [('readonly', True)]},
    )

    bank_id = fields.Many2one(
        comodel_name='res.bank',
        string='Bank',
        states={'close': [('readonly', True)]},
    )

    to_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='To Bank',
        states={'close': [('readonly', True)]},
        domain="['|', "
               "('company_id', '=', False), "
               "('company_id', '=', company_id)]"
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        states={'close': [('readonly', True)]},
        required=True
    )

    pay_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Pay',
        states={'close': [('readonly', True)]},
    )

    is_cash = fields.Boolean(
        string='Cash',
        states={'close': [('readonly', True)]},
    )

    is_payee_only = fields.Boolean(
        string='A/C Payee Only',
        states={'close': [('readonly', True)]},
    )

    is_bearer = fields.Boolean(
        string='Or Bearer',
        states={'close': [('readonly', True)]},
    )

    amount = fields.Float(
        string='Amount',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id'
    )

    reference = fields.Char(
        string='Reference',
        states={'close': [('readonly', True)]},
    )

    deposit_date = fields.Date(
        string='Deposit Date',
        states={'close': [('readonly', True)]},
    )

    close_date = fields.Date(
        string='Close Date',
        states={'close': [('readonly', True)]},
    )

    state = fields.Selection(
        string='Status',
        selection=lambda self: self._state_selection(),
        default='draft'
    )

    note = fields.Text(
        string='Note',
    )

    account_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry',
        copy=False,
        states={'close': [('readonly', True)]},
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        states={'close': [('readonly', True)]},
        default=_default_get_journal,
    )

    cancel_reason = fields.Char(
        string='Cancel Reason',
        readonly=True,
    )

    reject_reason = fields.Char(
        string='Reject Reason Note',
        readonly=True,
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pay_id = (
            self.partner_id.bank_ids and self.partner_id.bank_ids[0]
        ) or False

    def _state_selection(self):
        cheque_type = self._context.get('default_type', False)
        if self.type == 'vendor' or cheque_type == 'vendor':
            select = [('draft', 'Draft'),
                      ('to_approve', 'To Approve'),
                      ('to_deposit', 'To Deposit'),
                      ('deposit', 'Deposit'),
                      ('close', 'Close'),
                      ('cancel', 'Cancel'),
                      ('reject', 'Reject')
                      ]
        else:
            select = [('draft', 'Draft'),
                      ('to_deposit', 'To Deposit'),
                      ('deposit', 'Deposit'),
                      ('close', 'Close'),
                      ('cancel', 'Cancel'),
                      ('reject', 'Reject')
                      ]
        return select

#  <!-- customer -->
    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'to_deposit'
            })

    def action_to_deposit(self):
        for rec in self:
            if not rec.deposit_date:
                raise ValidationError(
                    _("The Deposit Date is required, please check before proceeding further."))
            rec.write({
                'state': 'deposit'
            })

    def action_change_cheque(self):
        view = self.env.ref(
            'beecy_account_cheque.account_change_cheque_wizard_views')
        context = dict(self.env.context) or {}
        if context['default_type'] == 'customer':
            context['default_move_type'] = 'customer'
        else:
            context['default_move_type'] = 'vendor'

        return {
            'name': _('Account Cheque'),
            'view_mode': 'form',
            'res_model': 'account.change.cheque.wizard',
            'view_id': view.id,
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_close(self):
        for rec in self:
            account_move_id = self.env['account.move']
            if rec.type == 'customer':
                if not rec.close_date:
                    raise ValidationError(
                        _("The close date is required, please check."))
                account_move_id |= self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,
                    'date': rec.close_date,
                    'ref': rec.name or rec.reference,
                    'line_ids': [(0, 0, {
                        'account_id': rec.journal_id.suspense_account_id.id,
                        'partner_id': rec.partner_id.id,
                        'name': "เช็ครับล่วงหน้า",
                        'credit': rec.amount,
                        'debit': 0,
                    }), (0, 0, {
                        'account_id': rec.to_bank_id.account_id.id,
                        'partner_id': self.partner_id.id,
                        'name': f"เช็ครับ {self.partner_id.name} {self.name}",
                        'debit': rec.amount,
                        'credit': 0,
                    })]
                })
            elif rec.type == 'vendor':
                if not rec.close_date:
                    rec.close_date = datetime.utcnow().date()
                account_move_id |= self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,
                    'date': rec.close_date,
                    'ref': rec.name or rec.reference,
                    'line_ids': [(0, 0, {
                        'account_id': rec.from_bank_id.account_id.id,
                        'partner_id': rec.partner_id.id,
                        'name': "เช็คจ่ายล่วงหน้า",
                        'credit': rec.amount,
                        'debit': 0,
                    }),
                        (0, 0, {
                            'account_id': rec.journal_id.suspense_account_id.id,
                            'partner_id': rec.partner_id.id,
                            'name': f"เช็คจ่าย {rec.partner_id.name} {rec.name}",
                            'debit': rec.amount,
                            'credit': 0,
                        })]
                })
            rec.write({
                'state': 'close',
                'account_move_id': account_move_id.id
            })
            return True

    def action_cancel(self):
        ctx = dict(self.env.context)
        ctx.update({
            'active_model': 'account.cheque',
            'active_id': self.id,
            'state': 'cancel',
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

    def action_set_draft(self):
        for rec in self:
            rec.account_move_id.unlink()
            rec.write({
                'state': 'draft'
            })

# <!-- vendor -->

    # TODO: Draft template for task Beecy-291 without template **form_bank_id.template_id
    # can change action_account_cheque_report
    def action_print_cheque(self):
        for rec in self:
            if rec.state == 'draft':
                rec.write({
                    'state': 'to_approve'
                })
            return rec.env.ref(
                'beecy_account_cheque.action_account_cheque_report').report_action(rec)

    def action_approve(self):
        for rec in self:
            if not rec.name:
                raise ValidationError(
                    _("Please define your cheque number before proceeding further."))
            rec.write({
                'state': 'to_deposit'
            })

    def action_reject(self):
        ctx = dict(self.env.context)
        ctx.update({
            'active_model': 'account.cheque',
            'active_id': self.id,
            'state': 'reject',
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
