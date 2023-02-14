from odoo import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals)

        ctx = dict(self.env.context)
        debit_credit = 'debit' if self.payment_type == 'inbound' else 'credit'
        if 'offset_account_id' in ctx:
            if self.move_wht_ids:
                liquidity_line, *remain_data = res
                if 'offset_amount' in ctx:
                    suspense_line = liquidity_line.copy()
                    suspense_line.update({
                        'account_id': ctx.get('offset_account_id').id,
                        debit_credit: ctx.get('offset_amount')
                    })
                    liquidity_line[debit_credit] = liquidity_line[debit_credit] - \
                        ctx.get('offset_amount')
                    res = [liquidity_line, suspense_line, *remain_data]
                else:
                    liquidity_line['account_id'] = ctx.get(
                        'offset_account_id').id

            else:
                liquidity_line, receivable_payable = res
                if 'offset_amount' in ctx:
                    suspense_line = liquidity_line.copy()
                    suspense_line.update({
                        'account_id': ctx.get('offset_account_id').id,
                        debit_credit: ctx.get('offset_amount')
                    })
                    liquidity_line[debit_credit] = liquidity_line[debit_credit] - \
                        ctx.get('offset_amount')
                    res = [liquidity_line, suspense_line, receivable_payable]
                else:
                    liquidity_line['account_id'] = ctx.get(
                        'offset_account_id').id

        return res

    def _get_valid_liquidity_accounts(self):
        ctx = dict(self.env.context)
        if ('offset_account_id' in ctx) and ('offset_amount' not in ctx):
            return (
                ctx.get('offset_account_id'),
                self.journal_id.default_account_id,
                self.payment_method_line_id.payment_account_id,
                self.journal_id.company_id.account_journal_payment_debit_account_id,
                self.journal_id.company_id.account_journal_payment_credit_account_id,
                self.journal_id.inbound_payment_method_line_ids.payment_account_id,
                self.journal_id.outbound_payment_method_line_ids.payment_account_id,
            )
        else:
            return super()._get_valid_liquidity_accounts()

    @api.depends('move_id.line_ids.amount_residual',
                 'move_id.line_ids.amount_residual_currency',
                 'move_id.line_ids.account_id')
    def _compute_reconciliation_status(self):
        ''' Compute the field indicating if the payments are already reconciled with something.
        This field is used for display purpose (e.g. display the 'reconcile' button redirecting to the reconciliation
        widget).
        '''
        for pay in self:
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()
            if not pay.currency_id or not pay.id:
                pay.is_reconciled = False
                pay.is_matched = False
            elif pay.currency_id.is_zero(pay.amount):
                pay.is_reconciled = True
                pay.is_matched = True
            else:
                residual_field = 'amount_residual' if pay.currency_id == pay.company_id.currency_id else 'amount_residual_currency'
                if pay.journal_id.default_account_id and pay.journal_id.default_account_id in liquidity_lines.account_id:
                    # Allow user managing payments without any statement lines by using the bank account directly.
                    # In that case, the user manages transactions only using
                    # the register payment wizard.
                    pay.is_matched = True
                else:
                    ctx = dict(self.env.context)
                    if 'offset_account_id' in ctx:
                        pay.is_matched = True
                    else:
                        pay.is_matched = pay.currency_id.is_zero(
                            sum(liquidity_lines.mapped(residual_field)))

                reconcile_lines = (
                    counterpart_lines
                    + writeoff_lines).filtered(
                    lambda line: line.account_id.reconcile)
                pay.is_reconciled = pay.currency_id.is_zero(
                    sum(reconcile_lines.mapped(residual_field)))
