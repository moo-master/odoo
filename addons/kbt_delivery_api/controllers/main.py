import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class DeliveryController(http.Controller):

    @APIBase.api_wrapper(['kbt.sale-order-create'])
    @http.route('/delivery/update', type='json', auth='user')
    def delivery_update_api(self, **params):
        try:
            msg = self._check_delivery_values(**params)
            if msg:
                return {
                    'isSuccess': 'Fail',
                    'message': msg,
                    'code': requests.codes.server_error,
                    'invoice_number': params['so_orderreference'] or 'No Data',
                }
            self._update_delivery_order(**params)
            return {
                'isSuccess': 'Success',
                'code': requests.codes.no_content,
            }
        except requests.HTTPError as http_err:
            return {
                'isSuccess': 'Fail',
                'code': requests.codes.server_error,
                'message': str(http_err),
            }
        except Exception as error:
            return {
                'isSuccess': 'Fail',
                'code': requests.codes.server_error,
                'message': str(error),
            }

    def _check_delivery_values(self, **params):
        msg_list = []
        if not params.get('so_orderreference'):
            msg_list.append('so_orderreference: No Data')
        if not params.get('item'):
            msg_list.append('item: No Data')
        return msg_list

    def _update_delivery_order(self, **params):
        # print("\n\n paramsss", params)
        SaleOrder = request.env['sale.order']
        return SaleOrder
