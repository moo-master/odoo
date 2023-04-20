from odoo import models, fields


class WhtTypeLine(models.Model):
    _name = "wht.type.line"

    wht_type_id = fields.Many2one(
        string='WHT',
        comodel_name='account.wht.type'
    )

    base_amount = fields.Float(
        string='Base Amount'
    )

    percent = fields.Float(
        string='Percent'
    )

    total = fields.Float(
        string='Total'
    )

    move_id = fields.Many2one(
        comodel_name='account.move'
    )

    purchase_id = fields.Many2one(
        comodel_name='purchase.order'
    )

    sale_id = fields.Many2one(
        comodel_name='sale.order'
    )
