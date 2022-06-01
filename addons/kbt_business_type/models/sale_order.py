from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_type_id = fields.Many2one(
        comodel_name='business.type',
        string='Sale Order Type',
        required=True,
        domain="[('x_type', '=', 'sale'), ('active', '=', True)]",
    )

    @api.model
    def create(self, vals):
        # print("\norigin-------", self._origin.so_type_id)
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        # if vals.get('name', _('New')) == _('New'):
            # seq_date = None
            # if 'date_order' in vals:
            # seq_date = fields.Datetime.context_timestamp(
            #     self, fields.Datetime.to_datetime(vals['date_order']))
            # print("\n id=======", self.so_type_id.x_sequence_id)
            # print("\n id////////", self.so_type_id)
            # print("\n VAlllllll", vals)
            # vals['name'] = self.so_type_id.next_by_id() or _('New')
        # print("\n id--------", vals['name'])
        result = super(SaleOrder, self).create(vals)
        return result
