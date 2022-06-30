from odoo import models, fields, api


class OrgLevelLine(models.Model):
    _name = 'org.level.line'
    _order = 'model_id'

    _sql_constraints = [
        ('org_level_line_move_type_id_uniq',
         'unique (model_id, move_type)',
         'Duplicate model_id and move_type in org.level.line not allowed !')]

    model_id = fields.Many2one(
        string='Model',
        comodel_name='ir.model',
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

    @api.depends('model_id')
    def _compute_model_id_readonly(self):
        for rec in self:
            rec.move_type.readonly = rec.model_id != "account.move"
