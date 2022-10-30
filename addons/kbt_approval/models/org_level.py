from odoo import models, fields, api


class OrgLevel(models.Model):
    _name = 'org.level'
    _order = 'write_date asc'
    _rec_name = 'display_name'

    _sql_constraints = [
        ('org_level_field_level_uniq',
         'unique (level)',
         'Duplicate level in org.level not allowed !'),
        ('org_level_line_move_type_id_uniq',
         'unique (line_ids.model_id, line_ids.move_type)',
         'Duplicate model_id and move_type in org.level.line not allowed !')]

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

    display_name = fields.Char(
        compute="_compute_new_display_name", store=True, index=True
    )

    @api.depends('display_name', 'description')
    def _compute_new_display_name(self):
        for rec in self:
            rec.display_name = str(rec.level) + ' ' + rec.description

    def approval_validation(self, model, amount, move_type):
        for line in self.line_ids:
            if model != 'account.move':
                if line.model_id.model == model:
                    return amount <= line.limit
            else:
                if line.move_type == move_type:
                    return amount <= line.limit
        return True
