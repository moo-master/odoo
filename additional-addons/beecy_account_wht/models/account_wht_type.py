from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountWhtType(models.Model):
    _name = 'account.wht.type'
    _description = 'Account Wht Type'
    _rec_name = 'display_name'
    _order = 'sequence'

    sequence = fields.Integer(
        'Sequence'
    )

    name = fields.Char(
        'Name',
        translate=True
    )

    display_name = fields.Char(
        'Description',
        compute='_compute_display_name',
        required=True,
    )
    percent = fields.Float(
        'Percent',
    )
    printed = fields.Char(
        'Printed',
    )
    short_name = fields.Char(
        'Short Name',
    )
    is_parent = fields.Boolean(
        'Is Parent',
        default=True,
        readonly=True,
    )
    parent_id = fields.Many2one(
        'account.wht.type',
        string='Parent',
    )
    other_type = fields.Selection(
        selection=[
            ('425', '4 (2.5) อื่นๆ'),
            ('600', '6 อื่นๆ (ระบุ)'),
        ],
        string='WHT Other Type',
        default=False
    )
    is_required_note = fields.Boolean(
        string='Require Note',
        default=False,
    )

    def _check_sequence(self, vals):
        if self.env['account.wht.type'].search(
                [('sequence', '=', vals.get('sequence'))]):
            raise ValidationError(
                _('Sequence of Withholding Tax Must be Unique.')
            )

    @api.model
    def create(self, vals):
        self._check_sequence(vals)
        return super(AccountWhtType, self).create(vals)

    def write(self, vals):
        self._check_sequence(vals)
        return super(AccountWhtType, self).write(vals)

    @api.depends('parent_id')
    def _onchange_parent(self):
        for rec in self:
            if rec.parent_id:
                rec.is_parent = True
            else:
                rec.is_parent = False

    def wht_calculator(self, amount):
        return amount * (self.percent / 100)

    @api.depends('name', 'percent')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'({rec.percent}%) {rec.name}'

    @api.model
    def _name_search(
            self,
            name='',
            args=None,
            operator='ilike',
            limit=100,
            name_get_uid=None):
        args = args or []
        args += ['|', ('percent', operator, name), ('name', operator, name)]
        return super(
            AccountWhtType,
            self)._name_search(
            name,
            args,
            operator,
            limit=limit)
