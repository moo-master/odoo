from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_address = fields.Text(
        string='Address',
    )

    x_partner_name = fields.Char(
        string='Partner Name',
    )
    is_admin = fields.Boolean(
        compute="_compute_is_admin"
    )

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        moves.write({
            'x_address': self.x_address,
            'x_partner_name': self.x_partner_name,
        })
        return moves

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.x_address = f"{self.partner_id.street or ''} {self.partner_id.street2 or ''} " +\
            f"{self.partner_id.city or ''} {self.partner_id.state_id.name or ''} " +\
            f"{self.partner_id.country_id.name or ''} {self.partner_id.zip or ''}"
        self.x_partner_name = self.partner_id.name or ''

    @api.depends('partner_id')
    def _compute_is_admin(self):
        self.write({
            'is_admin': self.env.user.has_group('base.group_system')
        })
