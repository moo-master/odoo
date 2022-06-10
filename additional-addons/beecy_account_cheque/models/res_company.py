from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_customer_cheque_journal_id = fields.Many2one(
        string='Default Customer Cheque Journal',
        comodel_name='account.journal',
        ondelete='cascade',
    )

    default_vendor_cheque_journal_id = fields.Many2one(
        string='Default Vendor Cheque Journa',
        comodel_name='account.journal',
        ondelete='cascade',
    )
