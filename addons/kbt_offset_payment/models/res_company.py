from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    de_offset_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Offset Account',
    )
    de_offset_account_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default Offset Account Journal',
    )
