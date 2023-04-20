from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    de_offset_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Offset Account',
        related='company_id.de_offset_account_id',
        readonly=False
    )
    de_offset_account_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default Offset Account Journal',
        related='company_id.de_offset_account_journal_id',
        readonly=False
    )
