from odoo import models, fields, api


class Company(models.Model):
    _inherit = 'res.company'

    title_id = fields.Many2one(
        related="partner_id.title",
        store=True,
        readonly=False,
    )
    prefix = fields.Char(
        related="partner_id.prefix",
        store=True,
        readonly=False,
    )
    suffix = fields.Char(
        related="partner_id.suffix",
        store=True,
        readonly=False,
    )
    nationality = fields.Selection(
        related="partner_id.nationality",
        store=True,
        readonly=False,
    )
    branch = fields.Selection(
        related="partner_id.branch",
        store=True,
        readonly=False,
    )
    branch_code = fields.Char(
        related="partner_id.branch_code",
        store=True,
        readonly=False,
    )
    house_number = fields.Char(
        compute="_compute_address",
        inverse="_inverse_house_number",
    )
    village_number = fields.Char(
        compute="_compute_address",
        inverse="_inverse_village_number",
    )
    village = fields.Char(
        compute="_compute_address",
        inverse="_inverse_village",
    )
    building = fields.Char(
        compute="_compute_address",
        inverse="_inverse_building",
    )
    floor = fields.Char(
        compute="_compute_address",
        inverse="_inverse_floor",
    )
    room_number = fields.Char(
        compute="_compute_address",
        inverse="_inverse_room_number",
    )
    alley = fields.Char(
        compute="_compute_address",
        inverse="_inverse_alley",
    )
    sub_alley = fields.Char(
        compute="_compute_address",
        inverse="_inverse_sub_alley",
    )
    name_english = fields.Char(
        related="partner_id.name_english",
        store=True,
        readonly=False,
    )

    @api.onchange('branch')
    def _onchange_branch(self):
        branch_code = False
        if self.branch == 'hq':
            branch_code = '00000'
        self.branch_code = branch_code

    @api.onchange('title_id')
    def _onchange_title(self):
        title = self.title_id
        if title:
            self.prefix = title.prefix
            self.suffix = title.suffix

    def _get_company_address_field_names(self):
        res = super(Company, self)._get_company_address_field_names()
        res += [
            'house_number', 'village_number', 'village',
            'building', 'floor', 'room_number',
            'alley', 'sub_alley'
        ]
        return res

    def _inverse_house_number(self):
        for company in self:
            company.partner_id.house_number = company.house_number

    def _inverse_village_number(self):
        for company in self:
            company.partner_id.village_number = company.village_number

    def _inverse_village(self):
        for company in self:
            company.partner_id.village = company.village

    def _inverse_building(self):
        for company in self:
            company.partner_id.building = company.building

    def _inverse_floor(self):
        for company in self:
            company.partner_id.floor = company.floor

    def _inverse_room_number(self):
        for company in self:
            company.partner_id.room_number = company.room_number

    def _inverse_alley(self):
        for company in self:
            company.partner_id.alley = company.alley

    def _inverse_sub_alley(self):
        for company in self:
            company.partner_id.sub_alley = company.sub_alley
