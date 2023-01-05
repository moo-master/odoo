from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    offset_ids = fields.One2many(
        'offset.payment',
        'move_id',
        string='Offset'
    )

    total_offset = fields.Monetary(
        'Total Offset',
        currency_field='company_currency_id',
        compute='_compute_offset'
    )

    # pylint: disable=biszx-boolean-field-name
    x_offset = fields.Boolean(
        'Offset',
        related='partner_id.x_offset'
    )

    @api.depends('offset_ids')
    def _compute_offset(self):
        for rec in self:
            rec.total_offset = sum(rec.offset_ids.mapped('total_amount'))
