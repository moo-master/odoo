from odoo import models, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    so_orderreference = fields.Char(
        string='SO Interface',
        readonly=True,
    )

    delivery_datetime = fields.Datetime(
        string='Delivery Date',
    )

    service_name = fields.Char(
        string='Service Name',
    )

    product_serie_name = fields.Char(
        string='Product Serie Name',
    )

    is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    seq_line = fields.Integer(
        string='Seq Line',
    )

    model = fields.Char(
        string='Model',
    )

    serial = fields.Char(
        string='Serial',
    )

    note = fields.Char(
        string='Note',
    )

    with_id = fields.Char(
        string='With ID',
    )
