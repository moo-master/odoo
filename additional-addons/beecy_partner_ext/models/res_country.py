from odoo import models, api, _
from odoo.exceptions import UserError


class Country(models.Model):
    _inherit = 'res.country'

    @api.constrains('address_format')
    def _check_address_format(self):
        for record in self:
            if record.address_format:
                address_fields = self.env['res.partner']._formatting_address_fields() + [
                    'state_code',
                    'state_name',
                    'country_code',
                    'country_name',
                    'company_name',
                    'house_number',
                    'village_number',
                    'village',
                    'building',
                    'floor',
                    'room_number',
                    'alley',
                    'sub_alley']
                try:
                    record.address_format % {i: 1 for i in address_fields}
                except (ValueError, KeyError):
                    raise UserError(
                        _('The layout contains an invalid format key'))
