from odoo import models, fields


class AccountAccountGroup(models.Model):
    _name = 'account.account.group'
    _description = 'Account Group'
    _rec_name = 'name'
    _order = 'internal_group, sequence'

    name = fields.Char(
        string='Account Group',
        readonly=True,
    )
    internal_group = fields.Selection([
        ('net_sales', 'NET SALES'),
        ('net_revenue_from_sales', 'NET REVENUE FROM SALES'),
        ('contribution_at_std_var_cost', 'CONTRIBUTION AT STD. VAR.COST'),
        ('net_contribution', 'NET CONTRIBUTION'),
        ('gross_profit', 'GROSS PROFIT'),
        ('net_profit_before_interest', 'NET PROFIT BEFORE INTEREST'),
        ('net_profit_loss_before_tax_kin', 'NET PROFIT (LOSS) BEFORE TAX - KIN'),
        ('net_profit_loss_after_income_tax_kin',
         'NET PROFIT (LOSS) AFTER INCOME TAX - KIN'),
    ],
        string="Internal Group",
        readonly=True
    )
    sequence = fields.Integer(
        string='Sequence',
        readonly=True,
    )
