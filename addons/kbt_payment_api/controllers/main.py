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
        return msg_list

    def _create_update_payment(self, **params):
        data_params_lst = params['data']
        Partner = request.env['res.partner']
        PartnerBank = request.env['res.partner.bank']
        AccountPayment = request.env['account.payment']
        User = request.env.user

        for data in data_params_lst:
            vals = {}
            x_interface_id = Partner.search(
                [('x_interface_id', '=', data['x_interface_id'])])

            journal_code = AccountPayment.journal_id.search([
                ('code', '=', data['journal_code']),
                ('company_id', '=', User.company_id.id)])

            date_api = data['date'].split('/')
            date_data = '{0}-{1}-{2}'.format(
                date_api[0], date_api[1], date_api[2])

            vals = {
                'payment_type': data['payment_type'],
                'partner_id': x_interface_id.id,
                'journal_id': journal_code.id,
                'amount': data['amount'],
                'ref': data['ref'],
                'date': date_data,
            }

            if data['payment_type'] == 'outbound':
                partner_bank_id = PartnerBank.search(
                    [('partner_id', '=', x_interface_id.id),
                     ('acc_number', '=', data['partner_bank_code']),
                     ('bank_id.bic', '=', data['bank_code'])])
                vals['partner_bank_id'] = partner_bank_id.id

            acc_payment = AccountPayment.create(vals)
            acc_payment.action_post()
