from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    wht_line_ids = fields.One2many(
        comodel_name='wht.type.line',
        inverse_name='move_id',
        readonly=True
    )
    x_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string='X Invoice'
    )
    is_wht_exist = fields.Boolean(
        string='Is WHt Exist',
        compute='_compute_is_wht_exist',
    )

    @api.depends('line_ids')
    def _compute_is_wht_exist(self):
        for move in self:
            move.write({
                'is_wht_exist': any(move.line_ids.mapped('is_wht_line'))
            })


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_wht_line = fields.Boolean(
        string='Wht Line',
    )
