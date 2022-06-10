from datetime import datetime
from bahttext import bahttext

from odoo import fields, models, api, _


class AccountMove(models.Model):
    """
    Account Move
    """
    _inherit = 'account.move'

    move_type = fields.Selection(
        selection_add=[
            ('out_debit', 'Customer Debit Note'),
            ('in_debit', 'Vendor Debit Note'),
        ],
        ondelete={'out_debit': 'set default', 'in_debit': 'set default'}
    )
    reason_id = fields.Many2one(
        comodel_name='res.reason',
        string='Reason',
        tracking=True,
        states={'posted': [('readonly', True)]},
        domain=lambda self: self._domain_reason_id(),

    )
    invoice_ref_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice Ref',
        tracking=True,
        states={'posted': [('readonly', True)]},
    )
    old_invoice_no = fields.Char(
        string='Old Tax Invoice',
        states={'posted': [('readonly', True)]},
    )
    old_invoice_date = fields.Date(
        string='Old Tax Invoice Date',
        states={'posted': [('readonly', True)]},
    )
    old_invoice_amount = fields.Float(
        string='Old Tax Invoice Amount',
        states={'posted': [('readonly', True)]},
    )
    old_invoice_tax_amount = fields.Float(
        string='Old Tax Invoice Tax Amount',
        states={'posted': [('readonly', True)]},
    )
    credit_note_count = fields.Integer(
        'Count Journal Entries',
        compute='_compute_credit_debit_note_count',
        readonly=True,
        store=True,
        copy=False,
    )
    credit_note_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='invoice_ref_id',
        domain="[('move_type', in, ['in_refund', 'out_refund'])]",
        string='Credit  Note',
        tracking=True,
    )
    debit_note_count = fields.Integer(
        string='Debit Note Count',
        compute='_compute_credit_debit_note_count',
        readonly=True,
        store=True,
        copy=False,
    )
    debit_note_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='invoice_ref_id',
        domain="[('move_type', in, ['in_debit', 'out_debit'])]",
        string='Debit Note',
        tracking=True,
    )

    state = fields.Selection(
        selection_add=[
            ('draft',),
            ('to_approve', 'To Approve'),
            ('posted',),
            ('reject', 'Reject'),
            ('cancel',),
        ],
        ondelete={
            'to_approve': 'cascade',
            'reject': 'cascade',
        }
    )

    state_customer = fields.Selection(
        related='state',
        string='State Customer',
        help="""
            Use for show on view form only.
            If you want to modify Please follow
            the standard odoo field name = 'state'
        """
    )

    state_vendor = fields.Selection(
        related='state',
        string='State Vendor',
        help="""
            Use for show on view form only.
            If you want to modify Please follow
            the standard odoo field name = 'state'
        """
    )

    reject_reason_id = fields.Many2one(
        string='Reject Reason',
        comodel_name='res.reason',
        tracking=True,
    )

    approve_uid = fields.Many2one(
        comodel_name='res.users',
        string='Approve Person',
        readonly=True,
        ondelete='cascade',
    )

    approve_date = fields.Date(
        string='Approve Date',
        readonly=True,
    )

    reject_uid = fields.Many2one(
        comodel_name='res.users',
        string='Reject Person',
        readonly=True,
    )

    reject_date = fields.Date(
        string='Reject Date',
        readonly=True,
    )

    reject_reason = fields.Char(
        string='Reject Reason Note',
    )

    cn_dn_reason = fields.Char('Credit/Debit Note Reason')

    def _get_move_display_name(self, show_ref=False):
        # Override
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'out_debit': _('Draft Customer Debit'),
                'in_debit': _('Draft Vender Debit'),
                'entry': _('Draft Entry'),
            }[self.move_type]
            name += ' '
        if not self.name or self.name == '/':
            name += '(* %s)' % str(self.id)
        else:
            name += self.name
        return name + (show_ref and self.ref and ' (%s%s)' %
                       (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    def _domain_reason_id(self):
        move_type = self._context.get('default_move_type', False)
        domain = self.env['res.reason']._get_domain_reason(
            self._name,
            move_type
        )
        return domain

    def action_reverse(self):
        res = super(AccountMove, self).action_reverse()
        context = dict(self.env.context or {})
        if self.move_type == 'out_invoice':
            context['move_type'] = 'out_refund'
            context['model_name'] = 'account.move'
        elif self.move_type == 'in_invoice':
            context['move_type'] = 'in_refund'
            context['model_name'] = 'account.move'
        res.update({'context': context})
        return res

    @api.depends('credit_note_ids', 'debit_note_ids')
    def _compute_credit_debit_note_count(self):
        for rec in self:
            rec.credit_note_count = len(
                rec.credit_note_ids.filtered(
                    lambda r: r.move_type in [
                        'in_refund', 'out_refund']))
            rec.debit_note_count = len(
                rec.debit_note_ids.filtered(
                    lambda r: r.move_type in [
                        'in_debit', 'out_debit']))

    @api.depends('move_type', 'partner_id', 'company_id')
    def _compute_narration(self):
        super(AccountMove, self)._compute_narration()
        for move in self.filtered(lambda r: not r.narration):
            move.narration = ''

    def _onchange_invoice_discount(self):
        """
            Important Process!!
            To avoid compute prorate cyclic

            Re-compute on-top discount process via onchange api method
            Code: beecy_account_discount
        :return: None
        """
        pass

    def action_credit_debit_note_view(self):
        ac_type = self.env.context.get('account_type', False)
        if ac_type == 'credit':
            domain = [('invoice_ref_id', '=', self.id)]
            if self.move_type == 'in_invoice':
                domain.append(['move_type', '=', 'in_refund'])
                context = {'default_move_type': 'in_refund'}
            else:
                domain.append(['move_type', '=', 'out_refund'])
                context = {'default_move_type': 'out_refund'}
            return {
                'name': _('Credit Note'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': domain,
                'context': context,
                'target': 'current',
            }
        elif ac_type == 'debit':
            domain = [('invoice_ref_id', '=', self.id)]
            if self.move_type == 'in_invoice':
                domain.append(['move_type', '=', 'in_debit'])
                context = {'default_move_type': 'in_debit'}
            else:
                domain.append(['move_type', '=', 'out_debit'])
                context = {'default_move_type': 'out_debit'}
            return {
                'name': _('Debit Note'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': domain,
                'context': context,
                'target': 'current',
            }
        return True

    def action_debit_note_reason_wizard(self):
        if self.move_type in ('out_invoice', 'out_refund', 'out_debit'):
            context = {
                'move_type': 'out_debit',
                'model_name': 'account.move',
                'default_move_type': self.move_type,
            }
        else:
            context = {
                'move_type': 'in_debit',
                'model_name': 'account.move',
                'default_move_type': self.move_type,
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Debit Notes'),
            'view_mode': 'form',
            'res_model': 'account.debit.note.reason',
            'target': 'new',
            'context': context,
        }

    def action_approve(self):
        self.update({
            'approve_uid': self.env.user.id,
            'approve_date': datetime.utcnow().date()
        })
        self.action_post()

    def action_reject_reason(self):
        self.update({
            'reject_uid': self.env.user.id,
            'reject_date': datetime.utcnow().date()
        })
        return True

    def action_to_approve(self):
        if self.user_has_groups('account.group_account_manager'):
            self.action_post()
        else:
            self.update({
                'state': 'to_approve'
            })

    def _get_seq_move_name(self):
        self.ensure_one()
        sequence_id = False
        if self.name in ['Draft', '/']:
            if self.move_type in ['out_invoice', 'in_invoice']:
                sequence_id = self.journal_id.invoice_sequence_id
            elif self.move_type in ['out_debit', 'in_debit'] and\
                    self.journal_id.is_debit_note_sequence:
                sequence_id = self.journal_id.debit_note_sequence_id
            elif self.move_type in ['out_refund', 'in_refund'] and\
                    self.journal_id.refund_sequence:
                sequence_id = self.journal_id.credit_note_sequence_id
        return sequence_id

    def action_post(self):
        sequence_id = self._get_seq_move_name()
        if sequence_id:
            self.name = sequence_id.next_by_id()
        super().action_post()

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        super()._compute_show_reset_to_draft_button()
        for move in self:
            move.show_reset_to_draft_button = (
                not move.restrict_mode_hash_table and move.state in (
                    'posted', 'cancel', 'reject'))

    def action_cancel_reject_reason_wizard(self):
        view = self.env.ref('beecy_reason.view_cancel_reject_reason_form')
        context = dict(
            self.env.context,
            move_type=self.move_type,
            model_name='account.move',
            state='reject'
        )
        return {
            'name': _('Reject Invoice'),
            'view_mode': 'form',
            'res_model': 'cancel.reject.reason',
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    def _amount_total_text(self, amount):
        return bahttext(amount)

    def is_purchase_document(self, include_receipts=False):
        res = super().is_purchase_document(include_receipts=False)
        return res

    @api.model
    def get_purchase_types(self, include_receipts=False):
        res = super().get_purchase_types(include_receipts=False)
        res.append('in_debit')
        return res

    @api.model
    def get_invoice_types(self, include_receipts=False):
        res = super().get_invoice_types(include_receipts=False)
        return res + ['out_debit', 'in_debit']

    @api.model
    def get_inbound_types(self, include_receipts=True):
        res = super().get_inbound_types(include_receipts=True)
        return res + ['out_debit', 'in_debit']

    @api.model
    def get_sale_types(self, include_receipts=False):
        res = super().get_sale_types(include_receipts=False)
        res.append('out_debit')
        return res

    def _creation_message(self):
        # OVERRIDE
        if not self.is_invoice(include_receipts=True):
            return super()._creation_message()
        return {
            'out_invoice': _('Invoice Created'),
            'out_refund': _('Credit Note Created'),
            'out_debit': _('Debit Note Created'),
            'in_invoice': _('Vendor Bill Created'),
            'in_refund': _('Refund Created'),
            'out_receipt': _('Sales Receipt Created'),
            'in_receipt': _('Purchase Receipt Created'),
            'in_debit': _('Purchase Debit Created'),
        }[self.move_type]

    @api.model
    def fields_view_get(self,
                        view_id=None,
                        view_type='tree',
                        toolbar=False,
                        submenu=False
                        ):
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        if toolbar:
            context = dict(self._context or {})
            move_type = context.get('default_move_type', [])
            data_report = self.prepare_data_report(move_type)
            if data_report:
                for report_id in data_report:
                    for report in res['toolbar']['print']:
                        if report_id == report['id']:
                            res['toolbar']['print'].remove(report)

        return res

    def prepare_data_report(self, move_type):
        data_report = []
        if move_type == 'out_invoice':
            data_report += self.prepare_data_invoice_report()

        if move_type == 'out_refund':
            data_report += self.prepare_data_credit_report()

        if move_type == 'out_debit':
            credit_data_report = self.prepare_data_credit_report()
            data_report += self.prepare_data_debit_report(credit_data_report)

        if move_type == 'in_invoice':
            report_templte = [
                'beecy_account.action_credit_note_report',
                'beecy_account.action_debit_note_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)

        if move_type == 'in_refund':
            report_templte = [
                'beecy_account.action_debit_note_report',
                'beecy_account.action_invoice_billing_delivery_report',
                'beecy_account.action_invoice_billing_billing_note_report',
                'beecy_account.action_tax_invoice_billing_note_report',
                'beecy_account.action_tax_invoice_delivery_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)

        if move_type == 'in_debit':
            report_templte = [
                'beecy_account.action_credit_note_report',
                'beecy_account.action_invoice_billing_delivery_report',
                'beecy_account.action_invoice_billing_billing_note_report',
                'beecy_account.action_tax_invoice_billing_note_report',
                'beecy_account.action_tax_invoice_delivery_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)

        if move_type in ['in_invoice', 'in_refund', 'in_debit']:
            report_templte = [
                'beecy_account.action_credit_note_report',
                'beecy_account.action_debit_note_report',
                'beecy_account.action_invoice_billing_delivery_report',
                'beecy_account.action_invoice_billing_billing_note_report',
                'beecy_account.action_tax_invoice_billing_note_report',
                'beecy_account.action_tax_invoice_delivery_report',
            ]
            data_report += self.prepare_action_menu_report(report_templte)
        if move_type:
            report_templte = self.env['ir.actions.report'].sudo().search([
                ('report_name', 'in', [
                    'base_accounting_kit.report_multiple_invoice_copies',
                    'base_accounting_kit.report_multiple_invoice'
                ])
            ]).ids or []
            data_report += report_templte
        return data_report

    def prepare_action_menu_report(self, report_templte):
        data_report = []
        for rec in report_templte:
            data_report.append(self.env.ref(rec).id)
        return data_report

    def prepare_data_invoice_report(self):
        data_report = []
        report_credit = self.env.ref(
            'beecy_account.action_credit_note_report')
        report_debit = self.env.ref(
            'beecy_account.action_debit_note_report')
        data_report.append(report_credit.id)
        data_report.append(report_debit.id)
        return data_report

    def prepare_data_credit_report(self):
        data_report = []
        report_tax_invoice = self.env.ref(
            'beecy_account.action_tax_invoice_billing_note_report')
        report_invoice_billing = self.env.ref(
            'beecy_account.action_invoice_billing_billing_note_report')
        report_invoice_delivery = self.env.ref(
            'beecy_account.action_tax_invoice_delivery_report')
        report_billing_delivery = self.env.ref(
            'beecy_account.action_invoice_billing_delivery_report')
        report_debit = self.env.ref(
            'beecy_account.action_debit_note_report')
        data_report.append(report_tax_invoice.id)
        data_report.append(report_invoice_billing.id)
        data_report.append(report_invoice_delivery.id)
        data_report.append(report_billing_delivery.id)
        data_report.append(report_debit.id)
        return data_report

    def prepare_data_debit_report(self, data_report):
        report_credit = self.env.ref(
            'beecy_account.action_credit_note_report')
        debit_tree = self.env.ref(
            'beecy_account.action_debit_note_report')
        data_report.remove(debit_tree.id)
        data_report.append(report_credit.id)
        return data_report

    # flake8: noqa: C901 - Odoo Standard Overiding
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        """
            ** This is origin Odoo15 Method **

            Compute the dynamic tax lines of the journal entry.

        :param  recompute_tax_base_amount: Flag forcing only the recomputation
                of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            """
                Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by
                    '_get_tax_grouping_key_from_tax_line' or
                    '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            """
            return '-'.join(str(v) for v in grouping_dict.values())

        taxes_map = {}
        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist,
                # we only need one to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====

        for line in self.line_ids.filtered(
            lambda l: not l.tax_repartition_line_id
        ):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            # Overide statement
            # See module: beecy_account_discount
            compute_all_vals = line._compute_base_line_taxes()
            # origin
            # compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on baseline
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(
                    line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line']
                tax_repartition_line = tax_repartition_line.browse(
                    tax_vals['tax_repartition_line_id']
                )
                tax = tax_repartition_line.invoice_tax_id or \
                    tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })

                tax_base_amount = self._get_base_amount_to_display(
                    tax_vals['base'], tax_repartition_line, tax_vals['group']
                )
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += tax_base_amount
                taxes_map_entry['grouping_dict'] = grouping_dict
        # ==== Pre-process taxes_map ====

        taxes_map = self._preprocess_taxes_map(taxes_map)
        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and \
                    not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue
            currency = self.env['res.currency'].browse(
                taxes_map_entry['grouping_dict']['currency_id']
            )
            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = currency._convert(
                taxes_map_entry['tax_base_amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self)
            )
            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    amount = tax_base_amount
                    taxes_map_entry['tax_line'].tax_base_amount = amount
                continue

            balance = currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }
            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and \
                    self.env['account.move.line'].new or \
                    self.env['account.move.line'].create

                tax_repartition_line = self.env['account.tax.repartition.line']
                tax_repartition_line = tax_repartition_line.browse(
                    taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                )
                tax = tax_repartition_line.invoice_tax_id or \
                    tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'company_id': self.company_id.id,
                    'company_currency_id': self.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(
                    taxes_map_entry['tax_line']._get_fields_onchange_balance(
                        force_computation=True)
                )

    @api.depends('line_ids')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self:
            if move.move_type == 'out_debit':
                move.amount_untaxed_signed = abs(move.amount_untaxed_signed)
                move.amount_total_signed = abs(move.amount_total_signed)
                for rec in move.line_ids:
                    debit = rec.debit
                    credit = rec.credit
                    if rec.account_id.user_type_id.type == 'receivable':
                        rec.debit = rec.debit or credit
                        rec.credit = 0.0
                    else:
                        rec.debit = 0.0
                        rec.credit = rec.credit or debit
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_base_line_taxes(self):
        """
            This is origin ODOO15 Inner Function

            Compute taxes amounts both in company currency / foreign currency
            as the ratio between amount_currency & balance
            could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on
                compute_all(...)['taxes'] in multi-currency.

        :return:            The result of the compute_all method.
        """
        move = self.move_id
        if move.is_invoice(include_receipts=True):
            handle_price_include = True
            sign = -1 if move.is_inbound() else 1
            quantity = self.quantity
            is_refund = move.move_type in ('out_refund', 'in_refund')
            price_unit_wo_discount = sign * self.price_unit * (
                1 - (self.discount / 100.0)
            )
        else:
            handle_price_include = False
            quantity = 1.0
            tax_type = self.tax_ids[0].type_tax_use if self.tax_ids else None
            is_refund = any([
                tax_type == 'sale' and self.debit,
                tax_type == 'purchase' and self.credit
            ])
            price_unit_wo_discount = self.amount_currency

        return self.tax_ids._origin.with_context(
            force_sign=move._get_tax_force_sign()).compute_all(
            price_unit_wo_discount,
            currency=self.currency_id,
            quantity=quantity,
            product=self.product_id,
            partner=self.partner_id,
            is_refund=is_refund,
            handle_price_include=handle_price_include,
            include_caba_tags=move.always_tax_exigible,
        )

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        vals_list = self.recompute_create_line(vals_list)
        lines = super(models.Model, self).create(vals_list)

        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves.filtered(lambda m: m.state
                       == 'posted')._check_fiscalyear_lock_date()
        lines.filtered(lambda l: l.parent_state
                       == 'posted')._check_tax_lock_date()
        moves._synchronize_business_models({'line_ids'})
        return lines

    def recompute_create_line(self, vals_list):
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            # important to bypass the ORM limitation where monetary fields are
            # not rounded; more info in the commit message
            vals.setdefault(
                'company_currency_id',
                move.company_id.currency_id.id)

            # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
            # company.
            currency_id = (vals.get(
                'currency_id') or move.company_id.currency_id.id)
            if currency_id == move.company_id.currency_id.id:
                balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                vals.update({
                    'currency_id': currency_id,
                    'amount_currency': balance,
                })
            else:
                vals['amount_currency'] = vals.get('amount_currency', 0.0)

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(
                    vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ).get('price_subtotal', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        vals['amount_currency'],
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(
                            vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.move_type,
                        currency,
                        move.company_id,
                        move.date,
                    ))
        return vals_list
