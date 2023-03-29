from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OrgLevel(models.Model):
    _name = 'org.level'
    _order = 'level, write_date asc'
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

    def get_authorize(self, model):
        auth_model = self.line_ids.filtered(lambda l: l.model_id_name == model)
        if auth_model:
            return True
        if self.level - 1 < 0:
            raise ValidationError(
                _("You do not have authorize to approve '%s' model") %
                model)
        return self.search([('level', '<', self.level)],
                           order='level desc', limit=1).get_authorize(model)

    def approval_validation(
            self,
            model,
            amount,
            move_type,
            employee,
            approval):
        res = True
        for line in self.line_ids:
            if model != 'account.move':
                if line.model_id.model == model:
                    res = (amount <= line.limit) or line.is_last_level
            else:
                if line.move_type == move_type and line.model_id.model == model:
                    res = (amount <= line.limit) or line.is_last_level

        if not res:
            approval.append(employee.parent_id.id)
            employee.parent_id.level_id.approval_validation(
                model, amount, move_type, employee.parent_id, approval
            )

        return approval, res
