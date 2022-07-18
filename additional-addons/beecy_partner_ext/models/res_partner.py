from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    prefix = fields.Char(
        string="Prefix",
        required=False,
    )
    suffix = fields.Char(
        string="Suffix",
        required=False,
    )
    nationality = fields.Selection(
        string="Nationality",
        selection=[
            ('th', 'Thai'),
            ('other', 'Others'),
        ],
        required=False,
        default="th",
    )
    branch = fields.Selection(
        string="Branch",
        selection=[
            ('hq', 'Headquarter'),
            ('branch', 'Branch'),
        ],
        required=False,
        default="hq",
    )
    branch_code = fields.Char(
        string="Branch Code",
        required=False,
        size=5,
    )
    house_number = fields.Char(
        string="No.",
        required=False,
    )
    village_number = fields.Char(
        string="Moo",
        required=False,
    )
    village = fields.Char(
        string="Village",
        required=False,
    )
    building = fields.Char(
        string="Building",
        required=False,
    )
    floor = fields.Char(
        string="Floor",
        required=False,
    )
    room_number = fields.Char(
        string="Room No.",
        required=False,
    )
    alley = fields.Char(
        string="Alley",
        required=False,
    )
    sub_alley = fields.Char(
        string="Sub Alley",
        required=False,
    )
    name_english = fields.Char(
        string="Name English",
        required=False,
    )
    display_name = fields.Char(
        'Display Name',
        compute='_compute_display_name',
    )

    @api.onchange('branch')
    def _onchange_branch(self):
        branch_code = False
        if self.branch == 'hq':
            branch_code = '00000'
        self.branch_code = branch_code

    @api.onchange('title')
    def _onchange_title(self):
        title = self.title
        if title:
            self.prefix = title.prefix
            self.suffix = title.suffix

    @api.onchange('company_type')
    def _onchange_company_type_domain_title(self):
        self.title = False
        self.prefix = False
        self.suffix = False
        domain = [
            ('contact_type', '=', self.company_type)
        ]
        return {
            'domain': {'title': domain}
        }

    @api.depends('name', 'prefix', 'suffix')
    def _compute_display_name(self):
        for partner in self:
            name = partner.name
            if partner.prefix:
                name = partner.prefix + ' ' + name
            if partner.suffix:
                name = name + ' ' + partner.suffix
            partner.display_name = name

    def _prepare_display_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
            'house_number': self.house_number or '',
            'village_number': self.village_number or '',
            'village': self.village or '',
            'building': self.building or '',
            'floor': self.floor or '',
            'room_number': self.room_number or '',
            'alley': self.alley or '',
            'sub_alley': self.sub_alley or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format, args
