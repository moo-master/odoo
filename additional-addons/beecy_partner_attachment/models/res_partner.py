from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    sale_attachment_ids = fields.Many2many(
        string='Sales Attachments',
        comodel_name='ir.attachment',
        relation='partner_sale_attachments_rel',
        column1='partner_id',
        column2='attachment_id',
    )

    purchase_attachment_ids = fields.Many2many(
        string='Purchases Attachments',
        comodel_name='ir.attachment',
        relation='partner_purchase_attachments_rel',
        column1='partner_id',
        column2='attachment_id',
    )
