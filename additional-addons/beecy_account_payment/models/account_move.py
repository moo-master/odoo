from odoo import models, fields, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    beecy_payment_id = fields.Many2one(
        comodel_name='beecy.account.payment',
        string="New Payment",
        index=True,
        check_company=True,
        copy=False,
    )

    beecy_payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_beecy_payment_count',
    )

    def _compute_beecy_payment_count(self):
        for rec in self:
            payment_line = self.env['account.payment.line.invoice']
            payment_ids = payment_line.search([('invoice_id', '=', rec.id)])

            for rec_line in payment_ids:
                rec.write({'beecy_payment_id': rec_line.payment_id.id})

            rec.beecy_payment_count = len(self.beecy_payment_id) or 0

    def action_register_payment(self):
        self.check_inv_register_payment()
        line_invoice = self.prepare_account_payment_line()
        billing_note = self.env['account.billing.note']
        payment_id = self._create_account_payment(line_invoice, billing_note)
        if payment_id:
            self.write({
                'beecy_payment_id': payment_id.id,
            })
            # Customer
            if self.move_type in ['out_invoice', 'out_refund', 'out_debit']:
                result = self.env['ir.actions.act_window']._for_xml_id(
                    'beecy_account_payment.beecy_action_account_payments')
            elif self.move_type in ['in_invoice', 'in_refund', 'in_debit']:
                # Vendor
                result = self.env['ir.actions.act_window']._for_xml_id(
                    'beecy_account_payment.action_beecy_account_payments_payable')
            else:
                result = {'type': 'ir.actions.act_window_close'}

            res = self.env.ref(
                'beecy_account_payment.view_beecy_account_payment_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in
                                               result['views'] if
                                               view != 'form']
            else:
                result['views'] = form_view

            result.update({
                'name': 'Beecy Account Payment',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': payment_id.id,
                'domain': [('id', 'in', payment_id.ids)],
            })

            return result

    def check_inv_register_payment(self):
        partner_id = self.mapped('partner_id')
        if len(partner_id) > 1:
            raise ValidationError(
                _("You can only register payment for the same partner"))
        company_id = self.mapped('company_id')
        if len(company_id) > 1:
            raise ValidationError(
                _("You can't create payments for entries belonging"
                  " to different companies."))
        internal_type = self.mapped(
            'invoice_line_ids.account_id.user_type_id.type')
        if len(internal_type) > 1:
            raise ValidationError(
                _("You can't register payments for journal items being either"
                  " all inbound, either all outbound."))
        for rec in self:
            if not rec.invoice_line_ids:
                raise ValidationError(
                    _("You can't register a payment because there is nothing"
                      " left to pay on the selected journal items."))
            if any([rec.state != 'posted', rec.payment_state == 'paid']):
                raise ValidationError(
                    _("You can only register payment for posted journal"
                      " entries."))

    def prepare_account_payment_line(self):
        line_invoice = []
        for rec in self:
            val = (0, 0, {
                'invoice_id': rec.id,
                'amount_wht': rec.amount_wht,
                'amount_tobe_paid': rec.amount_residual,
            })
            line_invoice.append(val)
        return line_invoice

    def _create_account_payment(self, line_invoice, billing_note):
        cash = self.env['account.journal'].search(
            [('type', '=', 'cash')], limit=1)
        # wait for setting invoice journal
        payment_type = 'inbound'
        partner_id = billing_note.partner_id
        if not billing_note:
            payment_type = 'outbound' if self.move_type == 'in_invoice' else 'inbound'
            partner_id = self.partner_id
        payment_id = self.env['beecy.account.payment'].create({
            'partner_id': partner_id.id,
            'note': billing_note.name or ",".join([invoice.name for invoice in self]),
            'payment_type': payment_type,
            'journal_id': cash.id,
            'payment_line_invoice_ids': line_invoice
        })
        payment_id._onchange_payment_line_invoice_ids()
        return payment_id

    def action_payment_view(self):
        action = False
        if self.move_type in ['out_invoice', 'out_refund', 'out_debit']:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'beecy_account_payment.action_beecy_account_payments_payable')
            action['domain'] = [('id', 'in', self.beecy_payment_id.ids)]
        elif self.move_type in ['in_invoice', 'in_refund', 'in_debit']:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'beecy_account_payment.beecy_action_account_payments')
            action['domain'] = [('id', 'in', self.beecy_payment_id.ids)]

        if action:
            return action
        else:
            return False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    beecy_payment_id = fields.Many2one(
        related='move_id.beecy_payment_id',
    )
