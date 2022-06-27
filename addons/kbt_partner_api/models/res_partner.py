from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    x_interface_id = fields.Char(
        string='Partner Interface',
        readonly=True,
    )

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
    )

    @api.depends('x_interface_id')
    def _compute_x_interface_id(self):
        for rec in self:
            if rec.x_interface_id:
                rec.ref = rec.x_interface_id

    @api.depends('x_is_interface')
    def _compute_x_is_interface(self):
        for rec in self:
            rec.ref.readonly = rec.x_is_interface
