import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class PaymentDataController(http.Controller):

    @APIBase.api_wrapper(['kbt.payment'])
    @http.route('/create_payment', type='json', auth='user')
    def payment_api(self, **params):
        try:
            msg = self._check_payment_values(**params)
            if msg:
                return {
                    'error': msg,
                    'code': requests.codes.server_error,
                }
            self._create_update_payment(**params)
            return {
                'code': requests.codes.no_content,
            }
        except requests.HTTPError as http_err:
            return {
                'code': requests.codes.server_error,
                'message': str(http_err),
            }
        except Exception as error:
            return {
                'code': requests.codes.server_error,
                'message': str(error),
            }

    def _check_payment_values(self, **params):
        msg_list = []
        if not params.get('data'):
            msg_list.append('Data: No Data')
        for data in params.get('data'):
            if not data.get('payment_type'):
                msg_list.append('payment_type: No Data')
            if not data.get('invoice_number'):
                msg_list.append('invoice_number: No Data')
            if not data.get('x_external_code'):
                msg_list.append('x_external_code: No Data')
            if not data.get('journal_code'):
                msg_list.append('journal_code: No Data')
            if not data.get('partner_bank_code'):
                msg_list.append('partner_bank_code: No Data')
            if not data.get('bank_code'):
                msg_list.append('bank_code: No Data')
            if not data.get('amount'):
                msg_list.append('amount: No Data')
            if not data.get('date'):
                msg_list.append('date: No Data')
            if not data.get('ref'):
                msg_list.append('ref: No Data')
        return msg_list

    def _create_update_payment(self, **params):
        data_params_lst = params.get('data')
        PartnerBank = request.env['res.partner.bank']
        AccountMove = request.env['account.move']
        AccountJournal = request.env['account.journal']
        PaymentRegister = request.env['account.payment.register']
        User = request.env.user

        for data in data_params_lst:
            vals = {}

            partner_bank = PartnerBank.search([
                ('acc_number', '=', data['partner_bank_code']),
                ('bank_id.bic', '=', data['bank_code']),
            ])

            journal_code = AccountJournal.search([
                ('code', '=', data['journal_code']),
                ('company_id', '=', User.company_id.id)])

            date_api = data['date'].split('/')
            date_data = '{0}-{1}-{2}'.format(
                date_api[0], date_api[1], date_api[2])

            acc_move = AccountMove.search([
                ('name', '=', data['invoice_number']),
                ('state', '=', 'posted'),
            ])
            res_action = acc_move.action_register_payment()
            ctx = res_action.get('context')
            vals = {
                'payment_type': data['payment_type'],
                'journal_id': journal_code.id,
                'amount': data['amount'],
                'payment_date': date_data,
                'partner_bank_id': partner_bank.id,
            }
            so_id = acc_move.mapped(
                'invoice_line_ids.sale_line_ids.order_id')
            po_id = acc_move.mapped(
                'invoice_line_ids.purchase_line_id.order_id')

            business_type = so_id.so_type_id \
                if acc_move.move_type == 'out_invoice' \
                else po_id.po_type_id
            if data['amount'] > acc_move.amount_residual \
                    and business_type.x_name != 'K-RENT':
                vals.update({
                    'payment_difference_handling': 'reconcile',
                    'writeoff_account_id':
                    business_type.default_gl_account_id.id,
                    'writeoff_label': 'Post-Difference',
                })
            payment_id = PaymentRegister.with_context(
                active_model=ctx['active_model'],
                active_ids=ctx['active_ids']).create(vals)
            payment_id.action_create_payments()
