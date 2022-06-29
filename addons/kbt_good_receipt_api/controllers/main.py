import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class ReceiptController(http.Controller):

    @APIBase.api_wrapper(['kbt.delivery-update'])
    @http.route('/delivery/update', type='json', auth='user')
    def goods_receipt_api(self, **params):
        try:
            msg = self._check_api_values(**params)
            if msg:
                return {
                    'isSuccess': 'Fail',
                    'message': msg,
                    'code': requests.codes.server_error,
                }
            res = self._create_goods_receipt(**params)
            return {
                'isSuccess': 'Success',
                'code': requests.codes.no_content,
                'invoice_number': res
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

    def _check_api_values(self, **params):
        msg_list = []
        for data in params['data']:
            if not data.get('so_orderreference'):
                msg_list.append('so_orderreference: No Data')
            if not data.get('item'):
                msg_list.append('item: No Data')
        return msg_list

    def _create_goods_receipt(self, **params):
        # Sale = request.env['sale.order']
        # SaleOrderLine = request.env['sale.order.line']
        # Product = request.env['product.product']
        # StockMove = request.env['stock.move']
        StockPick = request.env['stock.picking']
        # StockBack = request.env['stock.backorder.confirmation']
        return StockPick
