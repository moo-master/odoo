from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_module_beecy_account_payment_customer_steps = fields.Boolean(
        string='Customer Payment Approval Steps',
        related='company_id.is_module_beecy_account_payment_customer_steps',
        readonly=False
    )

    beecy_account_payment_customer_steps = fields.Selection(
        string='Customer Payment Approval Steps Selection',
        related='company_id.beecy_account_payment_customer_steps',
        readonly=False
    )

    is_module_beecy_account_payment_vendor_steps = fields.Boolean(
        string='Vendor Payment Approval steps',
        related='company_id.is_module_beecy_account_payment_vendor_steps',
        readonly=False
    )

    beecy_account_payment_vendor_steps = fields.Selection(
        string='Vendor Payment Approval Steps',
        related='company_id.beecy_account_payment_vendor_steps',
        readonly=False
    )

    ap_wht_default_account_id = fields.Many2one(
        'account.account',
        string='AP WHT Account',
        related='company_id.ap_wht_default_account_id',
        readonly=False
    )
    ar_wht_default_account_id = fields.Many2one(
        'account.account',
        string='AR WHT Account',
        related='company_id.ar_wht_default_account_id',
        readonly=False
    )

    @api.onchange('is_module_beecy_account_payment_customer_steps')
    def _onchange_payment_customer_step(self):
        if not self.is_module_beecy_account_payment_customer_steps:
            self.beecy_account_payment_customer_steps = False
        else:
            self.is_module_beecy_account_payment_vendor_steps = False
            self.beecy_account_payment_customer_steps = 'one_step'

    @api.onchange('is_module_beecy_account_payment_vendor_steps')
    def _onchange_payment_vendor_step(self):
        if not self.is_module_beecy_account_payment_vendor_steps:
            self.beecy_account_payment_vendor_steps = False
        else:
            self.is_module_beecy_account_payment_customer_steps = False
            self.beecy_account_payment_vendor_steps = 'one_step'
