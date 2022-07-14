import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class DeliveryController(http.Controller):

    @APIBase.api_wrapper(['kbt.delivery_update'])
    @http.route('/delivery/update', type='json', auth='user')
    def delivery_update_api(self, **params):
        try:
            msg = self._check_delivery_values(**params)
            if msg:
                return {
                    'isSuccess': False,
                    'message': msg,
                    'code': requests.codes.bad_request,
                }
            res = self._update_delivery_order(**params)
            return {
                'isSuccess': True,
                'code': requests.codes.all_ok,
                'invoice_number': res
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

    def _check_delivery_values(self, **params):
        msg_list = []
        for data in params['data']:
            if not data.get('so_orderreference'):
                msg_list.append('so_orderreference: No Data')
            if not data.get('item'):
                msg_list.append('item: No Data')
        return msg_list

    def _update_delivery_order(self, **params):
        AccountMove = request.env['account.move']
        Sale = request.env['sale.order']
        SaleOrderLine = request.env['sale.order.line']
        Product = request.env['product.product']
        StockMove = request.env['stock.move']
        StockPick = request.env['stock.picking']
        StockBack = request.env['stock.backorder.confirmation']
        SaleInvoice = request.env['sale.advance.payment.inv']

        response_api = []
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
                ('state', 'in', ['assigned', 'confirmed']),
            ])

            for item in data['item']:
                product_id = Product.search([
                    ('default_code', '=', item['product_id']),
                ])
                sale_line = SaleOrderLine.search([
                    ('order_id', '=', sale_order.id),
                    ('sequence', '=', item['seq_line']),
                    ('product_id', '=', product_id.id),
                ])
                stock_line = StockMove.search([
                    ('sale_line_id', '=', sale_line.id),
                ])
                stock_line.write({
                    'quantity_done':
                        stock_line.quantity_done + item['qty_done']
                })
            stock.write({
                'x_is_interface': True,
            })
            res = stock._pre_action_done_hook()
            if res is True:
                stock.button_validate()
            else:
                result = stock.button_validate()
                ctx = result.get('context')
                wiz = StockBack.create({
                    'pick_ids': ctx['default_pick_ids'],
                    'show_transfers': ctx['default_show_transfers'],
                }).with_context(button_validate_picking_ids=ctx['button_validate_picking_ids'])
                wiz.process()

            invoice_order = SaleInvoice.create({
                'advance_payment_method': 'delivered',
            }).with_context(active_ids=sale_order.id)
            res = invoice_order.create_invoices()
            acc_move = AccountMove.browse(res['res_id'])
            acc_move.action_post()
            response_api.append(acc_move.name)

        return response_api
