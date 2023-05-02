from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_address = fields.Text(
        'Address',
        copy=True
    )

    x_partner_name = fields.Char(
        string='Partner Name',
        copy=True
    )

    is_admin = fields.Boolean(
        compute="_compute_is_admin"
    )

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.company_type == 'person':
            if self.partner_id.parent_id:
                self.x_partner_name = self.partner_id.parent_id.name
                self.x_address = (
                    f"{self.partner_id.parent_id.street or ''} {self.partner_id.parent_id.street2 or ''} "
                    + f"{self.partner_id.parent_id.city or ''} {self.partner_id.parent_id.state_id.name or ''} "
                    + f"{self.partner_id.parent_id.country_id.name or ''} {self.partner_id.parent_id.zip or ''}")
            else:
                self.x_partner_name = self.partner_id.name
                self.x_address = (
                    f"{self.partner_id.street or ''} {self.partner_id.street2 or ''} "
                    + f"{self.partner_id.city or ''} {self.partner_id.state_id.name or ''} "
                    + f"{self.partner_id.country_id.name or ''} {self.partner_id.zip or ''}")
        else:
            self.x_partner_name = self.partner_id.name
            self.x_address = (
                f"{self.partner_id.street or ''} {self.partner_id.street2 or ''} "
                + f"{self.partner_id.city or ''} {self.partner_id.state_id.name or ''} "
                + f"{self.partner_id.country_id.name or ''} {self.partner_id.zip or ''}")

    @api.depends('partner_id')
    def _compute_is_admin(self):
        self.write({
            'is_admin': self.env.user.has_group('base.group_system')
        })

    def action_post(self):
        for rec in self:
            super().action_post()
            rec._onchange_partner()
            return rec
