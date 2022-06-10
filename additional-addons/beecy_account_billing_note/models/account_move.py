from odoo import api, fields, models, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    billing_note_count = fields.Integer(
        compute='_compute_billing_note_count',
        string="Billing Note Count",
    )

    billing_note_ids = fields.Many2many(
        string='Billing Note',
        comodel_name='account.billing.note',
        copy=False,
    )

    @api.depends('billing_note_ids')
    def _compute_billing_note_count(self):
        for record in self:
            domain = [
                ('billing_note_id.partner_id', '=', record.partner_id.id),
                ('invoice_id', '=', record.id),
                ('billing_note_id', 'not in', record.billing_note_ids.ids)
            ]
            billing_note = self.env['account.billing.note.line'].search(domain)
            billing_ids = billing_note.mapped('billing_note_id')
            for rec in billing_ids:
                record.write({
                    'billing_note_ids': [(4, rec.id)],
                })
            record.billing_note_count = len(record.billing_note_ids)

    def action_billing_note_ids(self):
        billing_note = self.mapped('billing_note_ids')
        action_billing = 'beecy_account_billing_note.action_billing_note'
        action = self.env.ref(action_billing).read()[0]
        if len(billing_note) > 1:
            action['domain'] = [('id', 'in', billing_note.ids)]
        elif len(billing_note) == 1:
            form_billing = 'beecy_account_billing_note.account_billing_note_view_form'
            form_view = [(self.env.ref(form_billing).id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [
                    (state, view)
                    for state, view in action['views'] if view != 'form'
                ]
            else:
                action['views'] = form_view
            action['res_id'] = billing_note.ids[0]
        return action

    def action_create_billing_note(self):
        partner_id = self.mapped('partner_id')
        if len(partner_id) > 1:
            raise ValidationError(
                _(
                    "The billing note should belong to the same customer,"
                    " right now you're selected the invoices that the partner is not the same"))
        elif len(self.mapped('billing_note_ids')):
            raise ValidationError(
                _("The invoices you selected had been billed"))
        elif len(self.filtered(
            lambda x: x.state != 'posted'
                or x.payment_state == 'paid')):
            raise ValidationError(
                _("There is nothing left to billing on the selected journal items"))

        billing_note = self.env['account.billing.note'].search(
            [('partner_id', '=', partner_id.id), ('state', '=', 'draft')])
        if len(billing_note) > 1:
            raise ValidationError(
                _("This customer had more than one pending billing note(draft),"
                    " you have to clear the billing note first"))
        billing_note_lines = []
        for record in self:
            billing_note_lines.append((0, 0, {
                'invoice_id': record.id,
                'note': record.narration,
                'invoice_payment_term_id': record.invoice_payment_term_id.id,
                'invoice_date': record.invoice_date_due,
                'currency_id': record.currency_id.id,
                'paid_amount': record.amount_residual or record.amount_total
            }))

        if billing_note:
            for record in self:
                record.write({
                    'billing_note_ids': [(4, billing_note.id)]
                })
            billing_note.write({
                'line_ids': billing_note_lines
            })
        elif not billing_note:
            payment_term = partner_id.property_payment_term_id
            days = 0
            if payment_term and len(payment_term.line_ids) >= 1:
                days = payment_term.line_ids[0].days
            Billing_note = self.env['account.billing.note']
            billing_note = Billing_note.create({
                'partner_id': partner_id.id,
                'payment_date': (datetime.utcnow() + timedelta(days=days)).date(),
                'payment_term_id': payment_term.id or False,
                'line_ids': billing_note_lines,
            })
            self.update({
                'billing_note_ids': [(4, billing_note.id)]
            })
        form_view_ref = self.env.ref(
            'beecy_account_billing_note.account_billing_note_view_form', False)
        tree_view_ref = self.env.ref(
            'beecy_account_billing_note.account_billing_note_view_tree', False)
        context = dict(
            self.env.context,
            active_id=billing_note.id,
            active_model='account.billing.note')
        return {
            'domain': [('id', 'in', [billing_note.id])],
            'name': 'Billing Note',
            'res_model': 'account.billing.note',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'context': context,
        }
