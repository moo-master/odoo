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
                    'error': msg,
                }
            self._create_update_partner(**params)
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

    def _check_partner_values(self, **params):
        msg_list = []
        data_params = params.get('data')
        for data in data_params:
            if not data.get('service_name'):
                msg_list.append('service_name: No Data')
            if not data.get('product_serie_name'):
                msg_list.append('product_serie_name: No Data')

        return msg_list

    def _create_update_partner(self, **params):
        Partner = request.env['res.partner']
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

            vals_dict = {
                'x_interface_id': data.get('x_interface_id'),
                'name': data.get('name'),
                'is_company': data.get('is_company'),
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
                'company_type': 'person',
                'property_account_receivable_id': account_receivable_id.id,
                'property_account_payable_id': account_payable_id.id
            }

            if not partner_id:
                Partner.create(vals_dict)
            else:
                partner_id.update(vals_dict)
