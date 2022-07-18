from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_address = fields.Text('Address')

    x_partner_name = fields.Char(
        string='Partner Name',
        readonly=True,
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices()
        res.write({
            'x_address': self.x_address
        })
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.x_address = f"{self.partner_id.street or ''} {self.partner_id.street2 or ''} " +\
            f"{self.partner_id.city or ''} {self.partner_id.state_id.name or ''} " +\
            f"{self.partner_id.country_id.name or ''} {self.partner_id.zip or ''}"
        self.x_partner_name = self.partner_id.name or ''
