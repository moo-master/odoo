import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class PartnerDataController(http.Controller):

    @APIBase.api_wrapper(['kbt.partner'])
    @http.route('/partner/data', type='json', auth='user')
    def res_partner_api(self, **params):
        try:
            msg = self._check_partner_values(**params)
            if msg:
                return {
                    'isSuccess': False,
                    'message': msg,
                    'code': requests.codes.bad_request,
                }
            self._create_update_partner(**params)
            return {
                'isSuccess': True,
                'code': requests.codes.all_ok,
            }
        except requests.HTTPError as http_err:
            return {
                'isSuccess': False,
                'code': requests.codes.bad_request,
                'message': str(http_err),
            }
        except Exception as error:
            return {
                'isSuccess': False,
                'code': requests.codes.bad_request,
                'message': str(error),
            }

    def _check_partner_values(self, **params):
        msg_list = []
        if not params.get('data'):
            msg_list.append('Data: No Data')
        return msg_list

    def _create_update_partner(self, **params):
        Partner = request.env['res.partner']
        ResBank = request.env['res.bank']
        data_params = params

        for data in data_params.get('data'):
            account_receivable_id = request.env['account.account'].search(
                [('code', '=', data.get('property_account_receivable_id')),
                 ('reconcile', '=', True),
                 ('company_id.company_code', '=', data.get('company_code'))
                 ])

            account_payable_id = request.env['account.account'].search(
                [('code', '=', data.get('property_account_payable_id')),
                 ('reconcile', '=', True),
                 ('company_id.company_code', '=', data.get('company_code'))
                 ])

            partner_id = Partner.search(
                [('x_interface_id', '=', data.get('x_external_code'))])

            if data.get('company_type') not in ['person', 'company']:
                raise ValueError(
                    "company_type must be 'person' or 'company'"
                )

            vals_dict = {
                'x_interface_id': data.get('x_external_code'),
                'name': data.get('name'),
                'company_type': data.get('company_type'),
                'type': data.get('type'),
                'street': data.get('street'),
                'street2': data.get('street2'),
                'zip': data.get('zip'),
                'city': data.get('city'),
                'state_id': data.get('state_id'),
                'country_id': data.get('country_id'),
                'vat': data.get('vat'),
                'phone': data.get('phone'),
                'mobile': data.get('mobile'),
                'email': data.get('email'),
                'website': data.get('website'),
                'category_id': data.get('category_id'),
                'property_account_receivable_id': account_receivable_id.id,
                'property_account_payable_id': account_payable_id.id,
                'x_is_interface': True,
            }

            if not partner_id:
                partner_id = Partner.create(vals_dict)
            else:
                partner_id.update(vals_dict)

            bank_id = ResBank.search([
                ('bic', '=', data.get('bank_id'))
            ], limit=1).id
            partner_bank = partner_id.mapped('bank_ids').mapped('bank_id')
            if bank_id in partner_bank.ids:
                res_bank = partner_id.mapped(
                    'bank_ids').filtered(lambda x: x.bank_id.id == bank_id)
                partner_id.write({
                    'bank_ids': [(1, res_bank.id, {
                        'acc_number': data.get('bank_acc_number'),
                    })]
                })
            else:
                partner_id.write({
                    'bank_ids': [(0, 0, {
                        'acc_number': data.get('bank_acc_number'),
                        'bank_id': bank_id
                    })]
                })
