from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_module_beecy_account_payment_customer_steps = fields.Boolean(
        string='Customer Payment Approval Steps',
    )

    beecy_account_payment_customer_steps = fields.Selection(
        selection=[
            ('one_step', 'One Step'),
        ],
        string='Customer Payment Approval Steps Module',
    )

    is_module_beecy_account_payment_vendor_steps = fields.Boolean(
        string='Vendor Payment Approval steps',
    )

    beecy_account_payment_vendor_steps = fields.Selection(
        selection=[
            ('one_step', 'One Step'),
            ('two_step', 'Two Step')],
        string='Vendor Payment Approval Steps Module',
    )

    ap_wht_default_account_id = fields.Many2one(
        'account.account',
        string='AP WHT Account',
    )
    ar_wht_default_account_id = fields.Many2one(
        'account.account',
        string='AR WHT Account',
    )
