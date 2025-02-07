from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ap_wht_default_account_pnd3_id = fields.Many2one(
        comodel_name='account.account',
        string='AP WHT Account (PND3)',
    )
    ap_wht_default_account_pnd53_id = fields.Many2one(
        comodel_name='account.account',
        string='AP WHT Account (PND53)',
    )
    ar_wht_default_account_id = fields.Many2one(
        comodel_name='account.account',
        string='AR WHT Account',
    )
    negotiate_duration = fields.Integer(
        string='Negotiate Duration',
        default=14,
    )
    payment_fee_percent = fields.Float(
        string='Payment Fee (%)',
        default=2.0,
    )
