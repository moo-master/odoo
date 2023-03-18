from odoo import models, fields


class OrgLevelLine(models.Model):
    _name = 'org.level.line'
    _order = 'model_id'

    model_id = fields.Many2one(
        string='Model',
        comodel_name='ir.model',
    )

    model_id_name = fields.Char(
        string='Model Name',
        related='model_id.model'
    )

    org_level_id = fields.Many2one(
        string='Org level id',
        comodel_name='org.level',
    )

    limit = fields.Float(
        string='Limitation',
    )

    move_type = fields.Selection(
        string='Move Type',
        selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ]
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain=[('type', '=', 'general')]
    )
