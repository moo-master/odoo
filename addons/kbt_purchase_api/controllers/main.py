import requests

from odoo import http
from odoo.http import request
from odoo.addons.rts_api_base.controllers.main import APIBase


class PurchaseController(http.Controller):

    @APIBase.api_wrapper(['kbt.purchase_create'])
    @http.route('/purchase/create', type='json', auth='user')
    def purchase_order_create_api(self, **params):
        try:
            self._create_purchase_order(**params)
            return {
                'isSuccess': True,
                'code': requests.codes.no_content,
            }
        except requests.HTTPError as http_err:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'error': str(http_err),
            }
        except Exception as error:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'error': str(error),
            }

    def _prepare_order_line(self, order_line, account_analytic_id, po_type):
        product_id = request.env['product.product'].search([
            ('default_code', '=', order_line.get('product_code')),
        ])

        product_type = product_id.detailed_type
        if product_type == 'service' and po_type not in ['K-RENT', 'K-MATCH']:
            raise ValueError("""
                Product %s is Service, Business Code must be K-RENT or K-MATCH
            """ % product_id.name)
        if product_type != 'service' and po_type != 'K-STORE':
            raise ValueError(
                "Product %s is not a Service, Business Code must be K-STORE"
                % product_id.name
            )

        vals = {
            'account_analytic_id': account_analytic_id.id,
            'product_id': product_id.id,
            'name': order_line.get('name'),
            'qty_received': 0,
            'product_qty': order_line.get('product_uom_qty'),
            'price_unit': order_line.get('price_unit'),
            'sequence': order_line.get('seq_line'),
        }

        if 'x_wht_id' in order_line:
            wht_seq = order_line.get('x_wht_id')
            wht_id = request.env['account.wht.type'].search([
                ('sequence', '=', wht_seq),
            ])

            if order_line.get('x_wht_id') and not wht_id:
                raise ValueError(
                    "Withholding Tax: %s have no data." % wht_seq
                )
            vals['x_wht_id'] = wht_id.id or False

        return vals

    def _create_purchase_order(self, **params):
        Purchase = request.env['purchase.order']
        Partner = request.env['res.partner']
        Account = request.env['account.analytic.account']
        Business = request.env['business.type']

        partner_ref = params.get('x_external_code')
        partner_id = Partner.search(
            [('x_interface_id', '=', partner_ref)])

        if not partner_id:
            partner_id = Partner.create({
                'x_interface_id': partner_ref
            })

        account_analytic_id = Account.search(
            [('name', '=', params.get('analytic_account'))])

        po_type = params.get('business_type_code').upper()
        po_type_id = Business.search([
            ('x_code', '=ilike', po_type)
        ])
        if not po_type_id:
            raise ValueError(
                "Business Code: %s have no data." % po_type
            )

        purchase_ref = params.get('x_purchase_ref')
        purchase_ref_id = Purchase.search([
            ('name', '=', purchase_ref)
        ])
        if purchase_ref_id:
            raise ValueError(
                "Purchase %s already exists." % purchase_ref
            )

        vals = {
            'partner_id': partner_id.id,
            'name': purchase_ref,
            'x_is_interface': params.get('x_is_interface'),
            'date_planned': params.get('receipt_date'),
            'po_type_id': po_type_id.id,
        }
        order_line_vals_list = [(0, 0, self._prepare_order_line(
            order_line, account_analytic_id, po_type))
            for order_line in params.get('lineItems')
        ]
        vals['order_line'] = order_line_vals_list

        purchase = Purchase.new(vals)
        purchase.onchange_partner_id()
        purchase_values = purchase._convert_to_write(purchase._cache)
        purchase_id = Purchase.create(purchase_values)
        purchase_id.button_confirm()

        return purchase_id.name

    @APIBase.api_wrapper(['kbt.purchase_update'])
    @http.route('/purchase/update', type='json', auth='user')
    def purchase_order_update_api(self, **params):
        try:
            res = self._update_purchase_order(**params)
            return {
                'isSuccess': True,
                'code': requests.codes.no_content,
                'invoice_number': res,
            }
        except requests.HTTPError as http_err:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'message': str(http_err),
                'invoice_number': params.get('x_purchase_ref') or "No Data"
            }
        except Exception as error:
            return {
                'isSuccess': False,
                'code': requests.codes.server_error,
                'message': str(error),
                'invoice_number': params.get('x_purchase_ref') or "No Data"
            }

    def _update_purchase_order(self, **params):
        Purchase = request.env['purchase.order']

        purchase_ref = params['x_purchase_ref']
        purchase_ref_id = Purchase.search([
            ('name', '=', purchase_ref),
            ('x_is_interface', '=', True)
        ])
        if not purchase_ref_id:
            raise ValueError(
                "Purchase %s does not exist." % purchase_ref
            )
        update_line_lst = []
        for order_line in params['lineItems']:
            seq_id = request.env['purchase.order.line'].search([
                ('sequence', '=', order_line.get('seq_line')),
                ('order_id', '=', purchase_ref_id.id)
            ])
            if order_line['qty_received'] + seq_id.qty_received >\
                    seq_id.product_qty:
                name = seq_id.name
                prod_qty = seq_id.product_uom_qty
                qty_recv = order_line['qty_received']
                raise ValueError(
                    f"Your ordered quantity of {name} is "
                    f"{prod_qty} and current delivered "
                    f"quantity is {qty_recv} your order "
                    f"quantity can’t more than "
                    f"{prod_qty - seq_id.qty_received}")
            else:
                update_line_lst.append(
                    (1, seq_id.id, {
                        'qty_received': seq_id.qty_received + order_line['qty_received']}))

        purchase_ref_id.update({
            'order_line': update_line_lst
        })
        purchase_ref_id.action_create_invoice()
        return purchase_ref_id.name
