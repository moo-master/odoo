from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        inverse_name='move_id',
        readonly=True
    )

    # @api.model_create_multi
    # def create(self, vals_list):
    #     super().create(vals_list)

    # def write(self, vals):
    #     super().write(vals)
