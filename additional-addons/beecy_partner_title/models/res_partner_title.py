from odoo import models, fields


class PartnerTitle(models.Model):
    _inherit = 'res.partner.title'

    contact_type = fields.Selection(
        string='Contact Type',
        selection=[
            ('person', 'Individual'),
            ('company', 'Company'),
        ],
        required=True,
        default='person',
    )
    prefix = fields.Char(
        string='Prefix'
    )
    suffix = fields.Char(
        string='Suffix'
    )
