import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class PaymentDataController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.payment'])
    @http.route('/payment/create', type='json', auth='user')
    def payment_api(self, **params):
        try:
            msg = self._check_payment_values(**params)
            if msg:
                return self._response_api(message=msg)
            self._create_update_payment(**params)
            return self._response_api(isSuccess=True)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_payment_values(self, **params):
        msg_list = []
        if not params.get('data'):
            msg_list.append('Data: No Data')
        for idx, data in enumerate(params.get('data')):
            msg_list += self._check_payment_line_values(data, idx)
        return msg_list

    def _check_payment_line_values(self, data, idx):
        ckeck_lst = {
            'payment_type',
            'invoice_number',
            'x_external_code',
            'journal_code',
            'partner_bank_code',
            'bank_code',
            'amount',
            'date',
            'ref'
        }
        data_key = set(data.keys())
        missing_value = ckeck_lst - data_key
        res = [f'Line {idx + 1} {val}: No Data' for val in missing_value]
        return res

    def _create_update_payment(self, **params):
        data_params_lst = params.get('data')
        PartnerBank = request.env['res.partner.bank']
        Partner = request.env['res.partner']
        AccountMove = request.env['account.move']
        AccountJournal = request.env['account.journal']
        PaymentRegister = request.env['account.payment.register']
        User = request.env.user

        for data in data_params_lst:
            vals = {}
            Partner.search(
                [('x_interface_id', '=', data['x_external_code'])])

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
