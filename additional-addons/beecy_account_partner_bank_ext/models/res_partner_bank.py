from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    account_id = fields.Many2one(
        string='Account',
        comodel_name='account.account',
        ondelete='cascade'
    )
