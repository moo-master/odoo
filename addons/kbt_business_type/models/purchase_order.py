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
        required=True,
        domain="[('x_type', '=', 'purchase'), ('active', '=', True)]",
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_id = None
            if not self.x_is_interface:
                seq_id = self.env['business.type'].search(
                    [('id', '=', vals['po_type_id'])]).x_sequence_id
                vals['name'] = seq_id.next_by_id() or '/'
        res = super(PurchaseOrder, self).create(vals)
        return res
