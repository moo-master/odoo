import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class DeliveryController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.delivery_update'])
    @http.route('/delivery/update', type='json', auth='user')
    def delivery_update_api(self, **params):
        try:
            msg = self._check_delivery_values(**params)
            if msg:
                return self._response_api(message=msg)
            res = self._update_delivery_order(**params)
            return self._response_api(isSuccess=True, invoice_number=res)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_delivery_values(self, **params):
        msg_list = []
        data = params
        if not data.get('so_orderreference'):
            msg_list.append('so_orderreference: No Data')
        if not data.get('item'):
            msg_list.append('item: No Data')
        check_lst = {
            'product_id',
            'seq_line',
            'qty_done',
        }
        for line in data['item']:
            key_line = set(line.keys())
            missing_val = check_lst - key_line
            msg_list += [f'Item {val}: No data' for val in missing_val]
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
        data = params
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
        if not stock:
            raise ValueError(
                "stock not found."
            )

        stock_move_lst = []
        for item in data['item']:
            product_id = Product.search([
                ('default_code', '=', item['product_id']),
            ])
            if not product_id:
                raise ValueError(
                    f"Product code({item.get('product_id')}) not found.")

            sale_line = SaleOrderLine.search([
                ('order_id', '=', sale_order.id),
                ('sequence', '=', item['seq_line']),
                ('product_id', '=', product_id.id),
            ])
            if not sale_line:
                raise ValueError(
                    f"Sale Order Line seq_line({item.get('seq_line')}) not found."
                )
            elif sale_line.product_id.detailed_type == 'service':
                raise ValueError(
                    "Can not update Service product by using Consume API.")
            stock_line = StockMove.search([
                ('sale_line_id', '=', sale_line.id),
                ('picking_id', '=', stock.id)
            ])
            if not stock_line:
                raise ValueError(
                    "stock_line not found."
                )
            if item['qty_done'] + \
                    sale_line.qty_delivered > sale_line.product_uom_qty:
                name = sale_line.name
                prod_qty = sale_line.product_uom_qty
                qty_deli = item['qty_done']
                total_qty = prod_qty - sale_line.qty_delivered
                raise ValueError(
                    f"Your ordered quantity of {name} is "
                    f"{prod_qty} and current delivered "
                    f"quantity is {qty_deli} your order "
                    f"quantity can’t more than {total_qty}")
            stock_move_lst.append((1, stock_line.id, {
                'quantity_done':
                    stock_line.quantity_done + item.get('qty_done')
            }))

        stock.write({
            'x_is_interface': True,
            'move_ids_without_package': stock_move_lst
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
        }).with_context(active_ids=sale_order.id, open_invoices=True)
        res = invoice_order.create_invoices()
        if res.get('res_id'):
            acc_move = AccountMove.browse(res['res_id'])
        else:
            acc_move = AccountMove.search(res['domain']).filtered(
                lambda y: y.state == 'draft'
            )
            if not acc_move:
                raise ValueError(
                    "acc_move not found."
                )
        for inv in acc_move:
            inv.action_post()
            response_api.append(inv.name)

        return response_api
