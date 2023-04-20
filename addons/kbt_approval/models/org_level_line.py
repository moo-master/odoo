from odoo import models, fields, api, _
from odoo.exceptions import UserError


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
    is_last_level = fields.Boolean(
        string="Last Level"
    )

    @api.onchange('is_last_level')
    def _onchange_last_level(self):
        if self.model_id:
            last_level = self.search(
                [('model_id', '=', self.model_id.id), ('is_last_level', '=', True)])
            if len(last_level) > 1:
                raise UserError(
                    _('Model %s is already have last level.') %
                    self.model_id_name)
