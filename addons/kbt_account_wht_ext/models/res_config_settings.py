from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ap_wht_default_account_pnd3_id = fields.Many2one(
        comodel_name='account.account',
        string='AP WHT Account (PND3)',
        related='company_id.ap_wht_default_account_pnd3_id',
        readonly=False
    )
    ap_wht_default_account_pnd53_id = fields.Many2one(
        comodel_name='account.account',
        string='AP WHT Account (PND53)',
        related='company_id.ap_wht_default_account_pnd53_id',
        readonly=False
    )
    ar_wht_default_account_id = fields.Many2one(
        comodel_name='account.account',
        string='AR WHT Account',
        related='company_id.ar_wht_default_account_id',
        readonly=False
    )
    negotiate_duration = fields.Integer(
        string='Negotiate Duration',
        related='company_id.negotiate_duration',
        readonly=False
    )
    payment_fee_percent = fields.Float(
        string='Payment Fee (%)',
        related='company_id.payment_fee_percent',
        readonly=False
    )
