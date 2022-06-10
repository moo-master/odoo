from odoo import fields, models


class PaymentAccountMoveWizard(models.TransientModel):
    _name = 'payment.account.move.wizard'
    _description = 'Payment Account Move Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice CN/DN',
    )
    name = fields.Char(
        string='Number',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    invoice_partner_display_name = fields.Char()
    invoice_date = fields.Date(
        string='Invoice/Bill Date',
    )
    invoice_due_date = fields.Date(
        string='Due Date',
    )
    amount_untaxed_signed = fields.Monetary(
        string='Untaxed Amount Signed',
    )
    amount_total_signed = fields.Monetary(
        string='Total Signed',
    )
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status',
    )
    move_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
        ('out_debit', 'Customer Debit Note'),
        ('in_debit', 'Vendor Debit Note'),
    ],
        string='Type', default="entry",
    )

    def action_confirm(self):
        ctx = dict(self.env.context)
        invoice = []
        payment_id = ctx.get('payment_id') or False
        beecy_payment = self.env['beecy.account.payment'].browse(
            payment_id
        )
        invoice_id_list = beecy_payment.payment_line_invoice_ids.invoice_id.ids
        for line in self:
            if line.move_id.id not in invoice_id_list:
                val = (0, 0,
                       {
                           'invoice_id': line.move_id.id,
                           'invoice_date_due_date': line.invoice_due_date,
                           'amount_untaxed': line.move_id.amount_untaxed,
                           'amount_total': line.move_id.amount_total,
                           'currency_id': line.currency_id,
                           'amount_wht': line.move_id.amount_wht,
                           'amount_residual': line.move_id.amount_residual,
                           'amount_tobe_paid': line.move_id.amount_residual,
                       }
                       )
                invoice.append(val)

        beecy_payment.update(
            {'payment_line_invoice_ids': invoice})
        beecy_payment._onchange_payment_line_invoice_ids()
        domain = [
            ('partner_id', '=', beecy_payment.partner_id.id),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('move_type', 'in', ctx.get('move_type')),
            ('amount_residual', '>', 0),
            ('billing_note_ids', '=', False)
        ]
        account_move_data = self.env['account.move'].search(domain)
        for acc in account_move_data:
            acc.beecy_payment_id = beecy_payment.id
