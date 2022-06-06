import requests

from odoo import http
from odoo.http import request


class SaleOrderDataController(http.Controller):

    @http.route('/sale/create', type='json', auth='user')
    def sale_order_api(self, **params):
        try:
            msg = self._check_sale_order_values(**params)
            if msg:
                return {
                    'error': msg,
                }
            partner_id = self._create_update_sale_order(**params)
            if partner_id:
                return {
                    'code': http.requests.codes.ok,
                    'Response': http.Response("OK", status=200)}
        except requests.HTTPError as http_err:
            return {
                'HTTP error': http_err,
            }
        except Exception as error:
            return {
                'error': error,
            }

    def _check_sale_order_values(self, **params):
        msg_list = []
        if not params.get('service_name'):
            msg_list.append('service_name: No Data')
        if not params.get('product_serie_name'):
            msg_list.append('product_serie_name: No Data')
        return msg_list

    def _prepare_order_line(self, order_line, is_new_line):
        product_id = request.env['product.product'].search(
            [('name', '=', order_line.get('product_id'))])
        if is_new_line:
            return {
                'product_id': product_id.id,
                'name': order_line.get('name'),
                'product_uom_qty': order_line.get('product_uom_qty'),
                'price_unit': order_line.get('price_unit'),
                'discount': order_line.get('discount'),
                'sequence': order_line.get('seq_line'),
                'note': order_line.get('note')
            }

        return {
            'qty_delivered': order_line['qty_delivered']
        }

    def _create_update_sale_order(self, **params):
        data = params
        vals = {}

        Sale = request.env['sale.order']
        Partner = request.env['res.partner']
        AccMove = request.env['account.move']

        so_orderreference = Sale.search(
            [('x_so_orderreference', '=', data.get('x_so_orderreference'))])

        if 'x_interface_id' in data:
            partner_id = Partner.search(
                [('x_interface_id', '=', data.get('x_interface_id'))])
            if not partner_id:
                partner_id = Partner.create(
                    {'name': data.get('x_interface_id')})
            vals['partner_id'] = partner_id.id

        if 'date_order' in data:
            date_order = data.get('date_order').split('-')
            datetime_order = '{0}-{1}-{2}'.format(
                date_order[2], date_order[1], date_order[0])
            vals['date_order'] = datetime_order

        if 'effective_date' in data:
            delivery_date = data.get('effective_date').split('-')
            delivery_datetime = '{0}-{1}-{2}'.format(
                delivery_date[2], delivery_date[1], delivery_date[0])
            vals['delivery_datetime'] = delivery_datetime

        if 'payment_term' in data:
            account_term = request.env['account.payment.term']
            account_term_id = account_term.search(
                [('name', '=', data.get('payment_term'))])
            vals['payment_term_id'] = account_term_id.id

        if 'analytic_account' in data:
            account_analytic = request.env['account.analytic.account']
            account_analytic_id = account_analytic.search(
                [('name', '=', data.get('analytic_account'))])
            vals['analytic_account_id'] = account_analytic_id.id

        if 'business_type' in data:
            business_type = request.env['business.type'].search([
                ('x_code', '=', data['business_type'])])
            vals['so_type_id'] = business_type.id

        vals['x_so_orderreference'] = data.get('x_so_orderreference')
        vals['x_is_interface'] = True

        order_line_vals_list = []
        for order_line in data.get('lineitems'):
            is_seq_line = request.env['sale.order.line'].search([
                ('sequence', '=', order_line.get('seq_line')),
                ('order_id', '=', so_orderreference.id)
            ])
            if not is_seq_line:
                order_line_vals_list.append(
                    (0, 0, self._prepare_order_line(order_line, True)))
            else:
                if order_line['qty_delivered'] > is_seq_line.product_uom_qty:
                    name = is_seq_line.name
                    uom_qty = is_seq_line.product_uom_qty
                    qty_deli = order_line['qty_delivered']
                    raise ValueError(f"Your ordered quantity of {name} is "
                                     f"{uom_qty} and current delivered "
                                     f"quantity is {qty_deli} your order "
                                     f"quantity can’t more than {uom_qty}")
                else:
                    order_line_vals_list.append(
                        (1, is_seq_line.id,
                         self._prepare_order_line(order_line, False)))
        vals['order_line'] = order_line_vals_list
        if not so_orderreference:
            sale = Sale.new(vals)
            sale.onchange_partner_id()
            sale_values = sale._convert_to_write(sale._cache)
            Sale.create(sale_values)
        else:
            so_orderreference.update(vals)
            order_line_lst = []
            for line in so_orderreference.order_line:
                order_line_lst.append((0, 0,
                                       self._prepare_invoice_line(line)))
            acc_move = AccMove.create({
                'partner_id': so_orderreference.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': order_line_lst,
            })
            acc_move.state = 'posted'

    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty_delivered,
            'price_unit': order_line.price_unit,
        }
