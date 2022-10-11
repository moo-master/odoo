from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        inverse_name='move_id',
        readonly=True
    )
    x_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='X Invoice'
    )
