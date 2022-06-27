import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class DeliveryController(http.Controller):

    @APIBase.api_wrapper(['kbt.delivery-update'])
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
        for data in params['data']:
            if not data.get('so_orderreference'):
                msg_list.append('so_orderreference: No Data')
            if not data.get('item'):
                msg_list.append('item: No Data')
        return msg_list

    def _update_delivery_order(self, **params):
        Sale = request.env['sale.order']
        SaleOrderLine = request.env['sale.order.line']
        Product = request.env['product.product']
        StockMove = request.env['stock.move']
        StockPick = request.env['stock.picking']

        for data in params['data']:
            sale_order = Sale.search([
                ('x_so_orderreference', '=', data.get('so_orderreference')),
                ('x_is_interface', '=', True),
            ])
            if not sale_order:
                raise ValueError(
                    "Sale Order %s does not exist." % data['so_orderreference']
                )
            stock = StockPick.search([
                ('sale_id', '=', sale_order.id),
            ])

            for item in data['item']:
                product_id = Product.search([
                    ('name', '=', item['product_id']),
                ])
                sale_line = SaleOrderLine.search([
                    ('order_id', '=', sale_order.id),
                    ('sequence', '=', item['seq_line']),
                    ('product_id', '=', product_id.id),
                ])
                stock = StockMove.search([
                    ('sale_line_id', '=', sale_line.id),
                ])
                stock.quantity_done = item['qty_done']
            stock.write({
                'x_is_interface': True,
            })
            stock.button_validate()
