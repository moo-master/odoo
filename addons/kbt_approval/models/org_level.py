from odoo import models, fields


class OrgLevel(models.Model):
    _name = 'org.level'
    _order = 'write_date asc'
    # _rec_name = level + role

    _sql_constraints = [('org_level_field_level_uniq', 'unique (level)',
                         'Duplicate level in org.level not allowed !')]

    level = fields.Integer(
        string='Level',
        required=True,
    )

    description = fields.Char(
        string='Description',
        required=True,
    )

    line_ids = fields.One2many(
        string='Configuration Lines',
        comodel_name='org.level.line',
        inverse_name='org_level_id',
    )

    def approval_vilidation(self, model, amount, move_type):
        for line in self.line_ids:
            if line.model_id == model.id and line.move_type == move_type:
                return amount < line.limit
