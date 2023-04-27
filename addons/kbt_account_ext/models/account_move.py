from odoo import models, fields, api, _
from odoo.exceptions import UserError

from bahttext import bahttext


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_type = fields.Selection(
        selection_add=[
            ('in_refund', 'Vendor Credit Note'),
            ('out_refund', 'Customer Credit Note'),
        ],
        ondelete={'in_refund': 'set default', 'out_refund': 'set default'}
    )
    x_old_invoice_amount = fields.Float(
        string='Old Invoice Amount',
        compute='_compute_old_invoice_amount',
        store=True,
    )
    x_wht_amount = fields.Float(
        string='WHT Amount',
        compute='_compute_old_invoice_amount',
        store=True,
    )
    x_real_amount = fields.Float(
        string='Real Amount',
    )
    x_diff_amount = fields.Float(
        string='Diff Amount',
    )
    reason_id = fields.Many2one(
        string='Reason',
        comodel_name='res.reason',
        domain=[('account_type', '=', 'out_refund')],
    )
    state = fields.Selection(
        selection_add=[
            ('reject', 'Reject'),
        ],
        ondelete={
            'reject': 'cascade',
        }
    )

    tax_type = fields.Selection(
        string="Tax Type",
        selection=[
            ('no_tax', 'No Tax'),
            ('tax', 'Tax'),
            ('deferred', 'Deferred Tax')
        ],
        compute="_compute_tax_type",
    )
    is_price_include = fields.Boolean(
        string='Price Include',
        compute='_compute_tax_in_out'
    )
    is_exempt = fields.Boolean(
        string='is Exempt',
        compute='_compute_tax_in_out',
    )

    @api.depends('invoice_line_ids.tax_ids')
    def _compute_tax_in_out(self):
        for rec in self:
            rec.write({
                'is_price_include': False,
                'is_exempt': True
            })
            if rec.invoice_line_ids:
                if rec.invoice_line_ids[0].tax_ids:
                    rec.write({
                        'is_price_include': rec.invoice_line_ids[0].tax_ids.price_include,
                        'is_exempt': rec.invoice_line_ids[0].tax_ids.is_exempt
                    })

    @api.constrains('date')
    def _check_date(self):
        for rec in self:
            if rec.move_type == 'in_invoice' and rec.date:
                if rec.invoice_date_due:
                    if rec.date > rec.invoice_date_due:
                        raise UserError(
                            _('Accounting date must be less than Due date.'))
                if rec.invoice_date:
                    if rec.date < rec.invoice_date:
                        raise UserError(
                            _('Accounting date must be greater than Bill date.'))

    @api.depends('invoice_line_ids.tax_ids')
    def _compute_tax_type(self):
        for rec in self:
            if rec.invoice_line_ids:
                if not rec.invoice_line_ids[0].tax_ids:
                    rec.write({
                        'tax_type': 'no_tax'
                    })
                elif rec.invoice_line_ids[0].tax_ids.is_exempt:
                    rec.write({
                        'tax_type': 'deferred'
                    })
                else:
                    rec.write({
                        'tax_type': 'tax'
                    })
            else:
                rec.write({
                    'tax_type': 'no_tax'
                })

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        if res.move_type != 'entry':
            taxs = res.invoice_line_ids.mapped('tax_ids')
            null_taxs = self.env['account.move.line']
            for line in res.invoice_line_ids:
                if not line.tax_ids and not line.display_type:
                    null_taxs = line
                    break
            if (taxs and null_taxs) or (len(taxs) > 1):
                raise UserError(_('Tax must be one and only one.'))
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.move_type != 'entry':
            if 'line_ids' in vals:
                taxs = self.invoice_line_ids.mapped('tax_ids')
                null_taxs = self.env['account.move.line']
                for line in self.invoice_line_ids:
                    if not line.tax_ids and not line.display_type:
                        null_taxs = line
                        break
                if (taxs and null_taxs) or (len(taxs) > 1):
                    raise UserError(_('Tax must be one and only one.'))
        return res

    def get_amount_total_text(self, amount):
        return bahttext(amount)

    @api.depends('x_real_amount')
    def _compute_old_invoice_amount(self):
        for move in self:
            invoice_id = move.reversed_entry_id
            move.write({
                'x_old_invoice_amount': invoice_id.amount_untaxed,
                'x_diff_amount': invoice_id.amount_untaxed - move.x_real_amount,
                'x_wht_amount': invoice_id.amount_wht,
            })

    @api.onchange('x_real_amount')
    def _onchange_x_real_amount(self):
        self.write({
            'x_diff_amount': self.x_old_invoice_amount - self.x_real_amount
        })

    # @api.multi
    def remove_menu_print(self, res, reports):
        # Remove reports menu
        report_ids = self.env['ir.actions.report']
        prints = []
        for report in reports:
            report_ids += self.env.ref(report, raise_if_not_found=False)
        if res.get('toolbar', {}).get('print', []):
            for rec in res.get('toolbar', {}).get('print', []):
                if rec.get('id', False) not in report_ids.ids:
                    prints.append(rec)
            res['toolbar']['print'] = prints
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        invoice_hide_menu = [
            'kbt_account_ext.action_kbt_debit_note_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
        credit_notes_hide_menu = [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
        refunds_hide_menu = [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_debit_note_report',
        ]
        bills_hide_menu = [
            'kbt_account_ext.action_kbt_invoice_report',
            'kbt_account_ext.action_kbt_invoice_tax_report',
            'kbt_account_ext.action_kbt_debit_note_report',
            'kbt_account_ext.action_kbt_credit_note_report',
        ]
        move_type = self._context.get('default_move_type')
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if res and view_type in ['tree', 'form']:
            # del menu report customer invoice
            if move_type == 'out_invoice':
                self.remove_menu_print(res, invoice_hide_menu)
            elif move_type == 'out_refund':
                self.remove_menu_print(res, credit_notes_hide_menu)
            elif move_type == 'in_refund':
                self.remove_menu_print(res, refunds_hide_menu)
            elif move_type == 'in_invoice':
                self.remove_menu_print(res, bills_hide_menu)
        return res
