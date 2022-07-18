from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )

    so_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Sale Order Type',
        required=True,
        domain="[('x_type', '=', 'sale'), ('active', '=', True)]",
    )

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_id = None
            if not self.x_is_interface:
                seq_id = self.env['business.type'].search(
                    [('id', '=', vals['so_type_id'])]).x_sequence_id
                vals['name'] = seq_id.next_by_id() or _('New')
        result = super(SaleOrder, self).create(vals)
        return result
