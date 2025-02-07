import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase

from datetime import datetime


class JournalController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.journal'])
    @http.route('/journal/create', type='json', auth='user')
    def journal_create_api(self, **params):
        try:
            self._create_journal(**params)
            return self._response_api(isSuccess=True)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _create_journal(self, **params):
        Sale = request.env['sale.order']
        Move = request.env['account.move']
        AccountJour = request.env['account.journal']
        ResCurrency = request.env['res.currency']
        User = request.env.user

        sale_id = Sale.search([
            ('x_so_orderreference', '=', params['x_so_orderreference'])
        ])
        if not sale_id:
            raise ValueError(
                "Sale Order Reference %s does not exist."
                % params['x_so_orderreference']
            )
        if not sale_id.invoice_ids:
            raise ValueError(
                "Sale Order Reference %s does not have Invoice."
                % params['x_so_orderreference']
            )
        move_id = sale_id.invoice_ids.sorted(lambda x: x.invoice_date)[0]

        currency_id = ResCurrency.search([('name', '=', params['currency'])])
        if not currency_id:
            raise ValueError(
                "Currency Not Found."
            )
        journal_id = AccountJour.search([
            ('code', '=', params['journal_code']),
            ('company_id', '=', User.company_id.id)])
        if not journal_id:
            raise ValueError(
                "Journal Not found."
            )
        if not params.get('x_status'):
            raise ValueError(
                "Missing x_status"
            )
        if 'auto_post' not in params:
            raise ValueError(
                "Missing auto_post"
            )

        date_data = datetime.strptime(params.get('account_date'), '%d-%m-%Y')
        if move_id.invoice_date > date_data.date():
            raise ValueError(
                "Date %s is back date of order date/accounting date." %
                date_data.strftime('%d-%m-%Y'))

        vals = {
            'ref': params['x_so_orderreference'],
            'date': date_data,
            'move_type': 'entry',
            'currency_id': currency_id.id or False,
            'journal_id': journal_id.id or False,
            'x_is_interface': True,
            'auto_post': params.get('auto_post')
        }
        self._check_balance_debit_credit(params.get('lineItems'))
        line_vals_lst = [(0, 0, self._prepare_line_ids(order_line, User))
                         for order_line in params.get('lineItems')]
        vals['line_ids'] = line_vals_lst
        journal_entry = Move.create(vals)
        if params.get('x_status') == 'posted':
            journal_entry.action_post()

    def _prepare_line_ids(self, line, user_id):
        account_id = request.env['account.account'].search([
            ('code', '=', line['account_code']),
            ('company_id', '=', user_id.company_id.id)])
        if not account_id:
            raise ValueError(
                f"Account code ({line['account_code']}) not found."
            )
        if account_id.deprecated:
            raise ValueError(
                f"Account code ({line['account_code']}) is deprecated."
            )

        if line.get('analytic_account'):
            account_analytic = request.env['account.analytic.account']
            account_analytic_id = account_analytic.search(
                [('code', '=', line.get('analytic_account'))])
            if not account_analytic_id:
                raise ValueError(
                    "Analytic Account Code Not Found."
                )
            account_analytic_id = account_analytic_id.id
        else:
            account_analytic_id = None

        return {
            'sequence': line['seq_line'],
            'account_id': account_id.id or False,
            'analytic_account_id': account_analytic_id,
            'debit': line['debit_amount'],
            'credit': line['credit_amount']
        }

    def _check_balance_debit_credit(self, line_items):
        debit = sum(line.get('debit_amount') for line in line_items)
        credit = sum(line.get('credit_amount') for line in line_items)
        if debit != credit:
            raise ValueError(
                f"Cannot create unbalanced journal entry. "
                f"Differences debit - credit: [{debit - credit}]"
            )
