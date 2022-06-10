from odoo import models, fields


class AccountBillingNoteInherit(models.Model):
    _inherit = 'account.billing.note'

    beecy_payment_ids = fields.One2many(
        comodel_name='beecy.account.payment',
        inverse_name='billing_note_id',
        string='Account Payment',
    )
    count_payment = fields.Integer(
        string='Count Payment',
        compute='_compute_count_payment'
    )

    def _compute_count_payment(self):
        for rec in self:
            rec.count_payment = len(rec.beecy_payment_ids.filtered(
                lambda r: r.state not in ['cancel', 'reject']
            ))

    def action_register_payment(self):
        account_move_ids = self.line_ids.filtered(
            lambda x: x.is_billing
        ).invoice_id.filtered(
            lambda x: x.state == 'posted'
        )
        account_move_ids.check_inv_register_payment()
        if account_move_ids:
            line_invoice = self.prepare_account_payment_line(account_move_ids)
            res = account_move_ids._create_account_payment(line_invoice, self)
            inv_ids = res.payment_line_invoice_ids.mapped(
                'invoice_id')
            for rec in inv_ids:
                rec.write({
                    'billing_note_ids': [(4, self.id)],
                    'beecy_payment_id': res.id,
                })
            if res:
                self.write({
                    'beecy_payment_ids': res.ids,
                })
                result = self.env['ir.actions.act_window']._for_xml_id(
                    'beecy_account_payment.beecy_action_account_payments')

                action = self.env.ref(
                    'beecy_account_payment.view_beecy_account_payment_form',
                    False)
                form_view = [(action and action.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for
                                                   state, view in
                                                   result['views'] if
                                                   view != 'form']

                result.update({
                    'name': 'Beecy Account Payment',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': res.id,
                    'domain': [('id', 'in', res.ids)],
                })

                return result

    def prepare_account_payment_line(self, account_move_ids):
        line_invoice = []
        for rec in account_move_ids:
            val = (0, 0, {
                'invoice_id': rec.id,
                'amount_wht': rec.amount_wht,
                'amount_tobe_paid': rec.amount_residual,
            })
            line_invoice.append(val)
        return line_invoice
