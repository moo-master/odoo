import requests
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class ReceiptController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.good_receipt'])
    @http.route('/good/receipt', type='json', auth='user')
    def good_receipt_api(self, **params):
        try:
            msg = self._check_api_values(**params)
            if msg:
                return self._response_api(message=msg)
            res = self._create_goods_receipt(**params)
            return self._response_api(isSuccess=True, purchase_ref=res)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_api_values(self, **params):
        data = params
        check_lst = {
            'purchase_ref',
            'Items',
        }
        missing_vals = check_lst - set(data.keys())
        msg_list = [f'{val}: Missing' for val in missing_vals]
        return msg_list

    def _create_goods_receipt(self, **params):
        data = params
        Purchase = request.env['purchase.order']
        Product = request.env['product.product']
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
        if not stock_id:
            raise ValueError(
                "Stock not found in Purchase Order %s." % data['purchase_ref']
            )

        update_line_lst = []
        for item in data['Items']:
            product_id = Product.search([
                ('default_code', '=', item.get('product_id'))])
            purchase_line = purchase_order.order_line.filtered(
                lambda x: x.sequence == item.get('seq_line')
                and x.product_id.id == product_id.id)
            stock_line = StockMove.search([
                ('picking_id', '=', stock_id.id),
                ('purchase_line_id', '=', purchase_line.id),
            ])
            if not stock_line:
                raise ValueError(
                    "stock_line not found."
                )
            update_line_lst.append((1, stock_line.id, {
                'quantity_done': item['qty_done']
            }))

        vals = {
            'x_bill_reference': data.get('x_bill_reference'),
            'x_is_interface': True,
            'move_ids_without_package': update_line_lst,
        }
        if params.get('x_bill_date'):
            x_bill_date = datetime.strptime(
                params.get('x_bill_date'), '%d-%m-%Y')
            vals.update({
                'x_bill_date': x_bill_date,
            })

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
        for inv in inv_ids.filtered(lambda z: z.state == 'draft'):
            inv.write({
                'ref': data.get('x_bill_reference'),
                'invoice_date': x_bill_date
                if params.get('x_bill_date') else False,
            })

        return data.get('purchase_ref')
