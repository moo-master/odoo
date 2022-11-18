from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # pylint: disable=biszx-boolean-field-name
    x_is_interface = fields.Boolean(
        string='Interface',
        readonly=True,
    )

    po_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Purchase Order Type',
        domain="[('x_type', '=', 'purchase'), ('is_active', '=', True)]",
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if not vals.get('x_is_interface') and vals.get('po_type_id'):
                seq_id = self.env['business.type'].search(
                    [('id', '=', vals['po_type_id'])]).x_sequence_id
                vals['name'] = seq_id.next_by_id()
        res = super(PurchaseOrder, self).create(vals)
        return res
