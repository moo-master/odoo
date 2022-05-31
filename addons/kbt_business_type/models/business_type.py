from odoo import models, fields


class BusinessType(models.Model):
    _name = "business.type"
    _description = "Business Type"

    x_name = fields.Char(
        string='x_name',
        required=True,
    )

    x_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase')],
        string='Type',
    )

    x_code = fields.Char(
        string='Code',
        required=True,
    )

    x_sequence_id = fields.Many2one(
        string='Sequence',
        comodel_name='ir.sequence',
        required=True,
    )

    x_revenue_account_id = fields.Many2one(
        string='Default Revenue Account',
        comodel_name='account.account',
        required=True,
    )

    active = fields.Boolean(
        string='active',
        default=True,
    )

    _sql_constraints = [
        (
            "x_code_uniq",
            "UNIQUE(x_code)",
            "You already have this Code.",
        )
    ]
