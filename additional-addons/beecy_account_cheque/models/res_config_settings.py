from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_cheque_journal_id = fields.Many2one(
        string='Default Customer Cheque Journal',
        comodel_name='account.journal',
        related='company_id.default_customer_cheque_journal_id',
        ondelete='cascade',
        readonly=False,
    )

    vendor_cheque_journal_id = fields.Many2one(
        string='Default Vendor Cheque Journa',
        comodel_name='account.journal',
        related='company_id.default_vendor_cheque_journal_id',
        readonly=False,
        ondelete='cascade',
    )
