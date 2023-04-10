from odoo import fields, models, api


class AccountWht(models.Model):
    _inherit = 'account.wht'

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment'
    )
    status = fields.Selection(
        selection_add=[
            ('cancel', 'Cancel'),
        ],
        ondelete={'cancel': 'set default'}
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Invoice Number',
        compute='_compute_get_move',
    )

    def action_cancel(self):
        self.status = 'cancel'

    @api.depends('invoice_line_ids')
    def _compute_get_move(self):
        for rec in self:
            invoices = rec.invoice_line_ids.mapped('move_id')
            rec.move_id = invoices[0]
