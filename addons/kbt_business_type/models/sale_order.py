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
        domain="[('x_type', '=', 'sale'), ('is_active', '=', True)]",
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if not vals.get('x_is_interface') and vals.get('so_type_id'):
                seq_id = self.env['business.type'].search(
                    [('id', '=', vals['so_type_id'])]).x_sequence_id
                vals['name'] = seq_id.next_by_id()
        result = super(SaleOrder, self).create(vals)
        return result
