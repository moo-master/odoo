import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class ReceiptController(http.Controller):

    @APIBase.api_wrapper(['kbt.good_receipt'])
    @http.route('/good/receipt', type='json', auth='user')
    def good_receipt_api(self, **params):
        try:
            msg = self._check_api_values(**params)
            if msg:
                return {
                    'isSuccess': False,
                    'message': msg,
                    'code': requests.codes.server_error,
                }
            self._create_goods_receipt(**params)
            return {
                'isSuccess': True,
                'code': requests.codes.no_content,
            }
        except requests.HTTPError as http_err:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'message': str(http_err),
            }
        except Exception as error:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'message': str(error),
            }

    def _check_api_values(self, **params):
        msg_list = []
        data = params
        if not data.get('purchase_ref'):
            msg_list.append('purchase_ref: No Data')
        if not data.get('x_bill_date'):
            msg_list.append('x_bill_date: No Data')
        if not data.get('x_bill_reference'):
            msg_list.append('x_bill_reference: No Data')
        if not data.get('Items'):
            msg_list.append('Items: No Data')
        else:
            for line in data.get('Items'):
                if not line.get('product_id'):
                    msg_list.append('Items product_id: No Data')
                if not line.get('name'):
                    msg_list.append('Items name: No Data')
                if not line.get('qty_done'):
                    msg_list.append('Items qty_done: No Data')
        return msg_list

    def _create_goods_receipt(self, **params):
        data = params
        Purchase = request.env['purchase.order']
        StockMove = request.env['stock.move']
        StockPick = request.env['stock.picking']
        StockBack = request.env['stock.backorder.confirmation']

        purchase_order = Purchase.search([
            ('name', '=', data.get('purchase_ref')),
            ('x_is_interface', '=', True),
        ])
        if not purchase_order:
            raise ValueError(
                "Purchase Order %s does not exist." % data['purchase_ref']
            )
        if not purchase_order.picking_ids:
            raise ValueError(
                "Purchase Order %s does not have Good Receipt."
                % data['purchase_ref']
            )

        stock_id = StockPick.search([
            ('purchase_id', '=', purchase_order.id),
            ('state', 'in', ['assigned', 'confirmed']),
        ])
        date_api = data.get('x_bill_date').split('/')
        x_bill_date = '{0}-{1}-{2}'.format(
            date_api[2], date_api[1], date_api[0])
        update_line_lst = []
        for item in data['Items']:
            purchase_line = purchase_order.order_line.filtered(
                lambda x: x.sequence == item['seq_line'])
            stock_line = StockMove.search([
                ('picking_id', '=', stock_id.id),
                ('purchase_line_id', '=', purchase_line.id),
            ])
            update_line_lst.append((1, stock_line.id, {
                'quantity_done': item['qty_done']
            }))

        vals = {
            'x_bill_date': x_bill_date,
            'x_bill_reference': data.get('x_bill_reference'),
            'x_is_interface': True,
            'move_ids_without_package': update_line_lst,
        }
        stock_id.write(vals)
        res = stock_id._pre_action_done_hook()
        if res is True:
            stock_id.button_validate()
        else:
            result = stock_id.button_validate()
            ctx = result.get('context')
            wiz = StockBack.create({
                'pick_ids': ctx['default_pick_ids'],
                'show_transfers': ctx['default_show_transfers'],
            }).with_context(
                button_validate_picking_ids=ctx['button_validate_picking_ids'])
            wiz.process()

        purchase_order.action_create_invoice()
        inv_ids = purchase_order.invoice_ids
        inv_ids.update({
            'ref': data.get('x_bill_reference'),
            'invoice_date': x_bill_date,
        })
        inv_ids.action_post()
