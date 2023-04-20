from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    account_group_id = fields.Many2one(
        'account.account.group',
        string='Account Group',
        related='account_id.account_group_id',
        store=True,
    )

    @api.depends('debit',
                 'credit',
                 'amount_currency',
                 'account_id',
                 'currency_id',
                 'move_id.state',
                 'company_id',
                 'matched_debit_ids',
                 'matched_credit_ids')
    def _compute_amount_residual(self):
        super()._compute_amount_residual()
        # Force save Data
        for line in self:
            if line.account_id.reconcile or line.account_id.internal_type == 'liquidity':
                reconciled_balance = sum(line.matched_credit_ids.mapped(
                    'amount')) - sum(line.matched_debit_ids.mapped('amount'))
                reconciled_amount_currency = sum(line.matched_credit_ids.mapped('debit_amount_currency'))\
                    - sum(line.matched_debit_ids.mapped('credit_amount_currency'))

                line.amount_residual = line.balance - reconciled_balance

                if line.currency_id:
                    line.amount_residual_currency = line.amount_currency - reconciled_amount_currency
                else:
                    line.amount_residual_currency = 0.0

                line.reconciled = (
                    line.company_currency_id.is_zero(
                        line.amount_residual) and (
                        not line.currency_id or line.currency_id.is_zero(
                            line.amount_residual_currency)) and (
                        line.matched_debit_ids or line.matched_credit_ids))
