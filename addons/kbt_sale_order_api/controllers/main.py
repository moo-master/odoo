import requests

from odoo import http
from odoo.http import request


class SaleOrderDataController(http.Controller):

    @http.route('/sale-order/data', type='json', auth='user')
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
        data_params = params.get('data')
        for data in data_params:
            if not data.get('service_name'):
                msg_list.append('service_name: No Data')
            if not data.get('product_serie_name'):
                msg_list.append('product_serie_name: No Data')
        return msg_list

    def _prepare_order_line(self, order_line):
        product_id = request.env['product.product'].search(
            [('name', '=', order_line.get('product_id'))])
        return {
            'product_id': product_id.id,
            'name': order_line.get('product_description'),
            'product_uom_qty': order_line.get('product_qty'),
            'price_unit': order_line.get('product_price'),
            'discount': order_line.get('discount'),
            'sequence': order_line.get('seq_line')
        }

    def _create_update_sale_order(self, **params):

        list_data_params = params.get('data')
        Sale = request.env['sale.order']
        Partner = request.env['res.partner']
        Company = request.env['res.company']

        for data in list_data_params:
            partner_id = Partner.search(
                [('name', '=', data.get('partner_id'))])

            if not partner_id:
                partner_id = Partner.create({'name': data.get('partner_id')})

            company_name_id = Company.search(
                [('company_code', '=', data.get('company_code'))])

            date_order = data.get('date_order').split('-')
            datetime_order = '{0}-{1}-{2}'.format(
                date_order[2], date_order[1], date_order[0])

            delivery_date = data.get('delivery_datetime').split('-')
            delivery_datetime = '{0}-{1}-{2}'.format(
                delivery_date[2], delivery_date[1], delivery_date[0])

            account_term = request.env['account.payment.term']
            account_term_id = account_term.search(
                [('name', '=', data.get('payment_term'))])

            account_analytic = request.env['account.analytic.account']
            account_analytic_id = account_analytic.search(
                [('name', '=', data.get('analytic_account'))])

            vals = {
                'partner_id': partner_id.id,
                'date_order': datetime_order,
                'delivery_datetime': delivery_datetime,
                'payment_term_id': account_term_id.id,
                'analytic_account_id': account_analytic_id.id,
                'company_id': company_name_id.id,
                'currency_id': company_name_id.currency_id.id,
                'so_orderreference': data.get('so_orderreference'),
                'is_interface': True
            }

            so_orderreference = Sale.search(
                [('so_orderreference', '=', data.get('so_orderreference'))])

            order_line_vals_list = []
            for order_line in data.get('lineitems'):
                is_seq_line = request.env['sale.order.line'].search([
                    ('sequence', '=', order_line.get('seq_line')),
                    ('order_id', '=', so_orderreference.id)
                ])

                if not is_seq_line:
                    order_line_vals_list.append(
                        (0, 0, self._prepare_order_line(order_line)))
                else:
                    order_line_vals_list.append(
                        (1, is_seq_line.id, self._prepare_order_line(order_line)))

            vals['order_line'] = order_line_vals_list
            if not so_orderreference:
                sale = Sale.new(vals)
                sale.onchange_partner_id()
                sale_values = sale._convert_to_write(sale._cache)
                Sale.create(sale_values)
            else:
                so_orderreference.update(vals)
