from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # pylint: disable=biszx-boolean-field-name
    x_offset = fields.Boolean(
        string='Offset Payment',
    )

    x_branch_name = fields.Char(
        string='Branch Name',
        size=5
    )

    @api.constrains('x_branch_name')
    def _check_numeric(self):
        if not self.x_branch_name.isdigit():
            raise UserError(_('Branch name must be numeric.'))
        return True
