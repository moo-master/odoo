from odoo import models, fields, api


class BusinessType(models.Model):
    _name = "business.type"
    _rec_name = "x_name"
    _description = "Business Type"

    x_name = fields.Char(
        string='Name',
    )

    x_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')],
        string='Type',
    )

    x_code = fields.Char(
        string='Code',
    )

    x_sequence_id = fields.Many2one(
        string='Sequence',
        comodel_name='ir.sequence',
    )

    x_revenue_account_id = fields.Many2one(
        string='Default Revenue Account',
        comodel_name='account.account',
    )

    default_gl_account_id = fields.Many2one(
        string='Default Post Difference Account (Gain)',
        comodel_name='account.account',
    )
    default_gl_loss_account_id = fields.Many2one(
        string='Default Post Difference Account (Loss)',
        comodel_name='account.account',
    )

    is_active = fields.Boolean(
        string='active',
        default=True,
    )

    is_unearn_revenue = fields.Boolean(
        string='Unearn Revenue'
    )

    _sql_constraints = [
        (
            "x_code_uniq",
            "UNIQUE(x_code)",
            "You already have this Code.",
        )
    ]

    @api.onchange('is_unearn_revenue')
    def _onchange_is_unearn_revenue(self):
        for rec in self:
            if not rec.is_unearn_revenue:
                rec.write({
                    'x_revenue_account_id': False
                })
