import requests
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class SaleOrderDataController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.sale_order_create'])
    @http.route('/sale/create', type='json', auth='user')
    def sale_order_create_api(self, **params):
        try:
            msg = self._check_sale_order_values(**params)
            if msg:
                return {
                    'isSuccess': False,
                    'code': requests.codes.bad_request,
                    'message': msg,
                }
            self._create_sale_order(**params)
            return self._response_api(isSuccess=True)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_sale_order_values(self, **params):
        msg_list = []
        return msg_list

    def _prepare_order_line(self, order_line):
        vals = {}
        if not order_line.get('product_id') and order_line.get('note'):
            vals = {
                'sequence': order_line.get('seq_line'),
                'name': order_line.get('note'),
                'display_type': "line_note",
            }
        elif order_line.get('product_id'):
            product_id = request.env['product.product'].search(
                [('default_code', '=', order_line.get('product_id'))])

            wht_id: int = product_id.wht_type_id.id
            if 'x_wht_id' in order_line:
                wht_id = request.env['account.wht.type'].search([
                    ('sequence', '=', (seq := int(order_line.get('x_wht_id') or 0))),
                ]).id
                if not wht_id and seq:
                    raise ValueError(
                        "Withholding Tax: %s have no data." % seq
                    )

            vals.update({
                'product_id': product_id.id,
                'name': order_line.get('name'),
                'product_uom_qty': order_line.get('product_uom_qty'),
                'price_unit': order_line.get('price_unit'),
                'discount': order_line.get('discount'),
                'sequence': order_line.get('seq_line'),
                'note': order_line.get('note'),
                'wht_type_id': wht_id,
            })
        else:
            raise ValueError(
                "This item is neither 'product' nor 'note'."
            )

        return vals

    def _create_sale_order(self, **params):
        data = params
        vals = {}

        Sale = request.env['sale.order']
        Partner = request.env['res.partner']
        Business = request.env['business.type']

        so_orderreference = Sale.search(
            [('x_so_orderreference', '=', data.get('x_so_orderreference'))])
        if so_orderreference:
            raise ValueError(
                "Sale Order %s already exists." % data['x_so_orderreference']
            )

        partner_id = Partner.search(
            [('x_interface_id', '=', data.get('x_external_code'))])
        if not partner_id:
            raise ValueError(
                "partner_id not found."
            )
        vals['partner_id'] = partner_id.id

        datetime_order = datetime.strptime(data.get('date_order'), '%d-%m-%Y')
        vals['date_order'] = datetime_order

        delivery_date = data.get('effective_date').split('-')
        delivery_datetime = '{0}-{1}-{2}'.format(
            delivery_date[2], delivery_date[1], delivery_date[0])
        vals['delivery_datetime'] = delivery_datetime

        account_term = request.env['account.payment.term']
        account_term_id = account_term.search(
            [('payment_term_code', '=', data.get('payment_term'))])
        if not account_term_id:
            raise ValueError(
                "Payment Term Code Not Found."
            )
        vals['payment_term_id'] = account_term_id.id

        account_analytic = request.env['account.analytic.account']
        account_analytic_id = account_analytic.search(
            [('code', '=', data.get('analytic_account'))])
        if not account_analytic_id:
            raise ValueError(
                "Analytic Account Code Not Found."
            )
        vals['analytic_account_id'] = account_analytic_id.id

        business_type = request.env['business.type'].search([
            ('x_code', '=', data['x_so_type_code'])])
        if not business_type:
            raise ValueError(
                "business_type not found."
            )
        if not business_type.is_active:
            raise ValueError(
                f"Business Type Code ({data['x_so_type_code']}) is inactive."
            )

        vals['so_type_id'] = business_type.id

        so_type = params.get('x_so_type_code').upper()
        so_type_id = Business.search([
            ('x_code', '=ilike', so_type)
        ])
        if not so_type_id:
            raise ValueError(
                "so_type_id not found."
            )
        vals['so_type_id'] = so_type_id.id

        vals['x_so_orderreference'] = data.get('x_so_orderreference')
        vals['x_is_interface'] = True
        vals['x_address'] = data.get('x_address')

        order_line_vals_list = [(0, 0, self._prepare_order_line(
            order_line))
            for order_line in params.get('lineItems')
        ]
        vals['order_line'] = order_line_vals_list

        sale = Sale.new(vals)
        sale.onchange_partner_id()
        sale_values = sale._convert_to_write(sale._cache)
        sale_id = Sale.create(sale_values)

        sale_id.action_confirm()
        sale_id.write({
            'name': params.get('x_so_orderreference'),
            'payment_term_id': account_term_id.id,
            'date_order': sale_id.date_order.replace(
                datetime_order.year, datetime_order.month, datetime_order.day),
        })

    @KBTApiBase.api_wrapper(['kbt.sale_order_update'])
    @http.route('/sale/update', type='json', auth='user')
    def sale_order_update_api(self, **params):
        try:
            msg = self._check_sale_order_values(**params)
            if msg:
                return self._response_api(message=msg)
            res = self._update_sale_order(**params)
            return self._response_api(isSuccess=True, invoice_number=res)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _update_sale_order(self, **params):
        Sale = request.env['sale.order']

        so_ref = params.get('x_so_orderreference')
        so_orderreference = Sale.search([
            ('x_so_orderreference', '=', so_ref),
            ('x_is_interface', '=', True)])
        if not so_orderreference:
            raise ValueError(
                "Sale Order Reference %s does not exist." % so_ref
            )

        update_line_lst = []
        for order_line in params['lineItems']:

            seq_id = so_orderreference.order_line.filtered(
                lambda x: x.sequence == order_line.get('seq_line')
                and not x.display_type)
            if not seq_id:
                raise ValueError(
                    f"Sale Order Line seq_line({order_line.get('seq_line')}) not found.")
            if seq_id.product_id.detailed_type != 'service':
                raise ValueError(
                    "Can not update Consume product by using Service API."
                )

            if order_line['qty_delivered'] + seq_id.qty_delivered >\
                    seq_id.product_uom_qty:
                name = seq_id.name
                prod_qty = seq_id.product_uom_qty
                qty_deli = order_line['qty_delivered']
                raise ValueError(
                    f"Your ordered quantity of {name} is "
                    f"{prod_qty} and current delivered "
                    f"quantity is {qty_deli} your order "
                    f"quantity can’t more than {prod_qty - seq_id.qty_delivered}")
            elif seq_id.product_id.detailed_type != 'service':
                raise ValueError(
                    "Can not update Consume product by using Service API.")
            update_line_lst.append(
                (1, seq_id.id, {
                    'qty_delivered':
                        seq_id.qty_delivered + order_line['qty_delivered']
                }))
        partner = so_orderreference.partner_id
        x_address = params.get('x_address') or (
            f"{partner.street or ''} {partner.street2 or ''} "
            + f"{partner.city or ''} {partner.state_id.name or ''} "
            + f"{partner.country_id.name or ''} {partner.zip or ''}"
        )
        x_partner_name = params.get('x_partner_name') or partner.name
        so_orderreference.update({
            'order_line': update_line_lst,
            'x_address': x_address,
            'x_partner_name': x_partner_name
        })
        move_id = so_orderreference._create_invoices()
        move_id.write({
            'x_is_interface': True,
            'x_partner_name': x_partner_name
        })
        move_id.action_post()
        return move_id.name
