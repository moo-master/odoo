from odoo import models, fields


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    account_group_id = fields.Many2one(
        'account.account.group',
        string='Account Group',
    )


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    account_group_id = fields.Many2one(
        'account.account.group',
        string='Account Group',
        related='crossovered_budget_id.account_group_id',
        store=True,
    )
