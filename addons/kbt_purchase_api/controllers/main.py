import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase


class PurchaseController(KBTApiBase):

    @KBTApiBase.api_wrapper(['kbt.purchase_create'])
    @http.route('/purchase/create', type='json', auth='user')
    def purchase_order_create_api(self, **params):
        try:
            self._create_purchase_order(**params)
            return self._response_api(isSuccess=True)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _prepare_order_lines(self, order_line):
        Account = request.env['account.analytic.account']

        account_analytic_id = Account.search(
            [('name', '=', order_line.get('analytic_account'))])
        if not account_analytic_id:
            raise ValueError(
                "account_analytic_id not found."
            )

        product_id = request.env['product.product'].search([
            ('default_code', '=', order_line.get('product_code')),
        ])
        if not product_id:
            raise ValueError(
                "product_id not found."
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
            if not wht_id:
                raise ValueError(
                    "wht_id not found."
                )

            if order_line.get('x_wht_id') and not wht_id:
                raise ValueError(
                    "Withholding Tax: %s have no data." % wht_seq
                )
            vals['x_wht_id'] = wht_id.id or False

        return vals

    def _create_purchase_order(self, **params):
        Purchase = request.env['purchase.order']
        Partner = request.env['res.partner']

        Business = request.env['business.type']

        partner_ref = params.get('x_external_code')
        partner_id = Partner.search(
            [('x_interface_id', '=', partner_ref)])

        if not partner_id:
            raise ValueError(
                "partner_id not found."
            )

        po_type = params.get('x_po_type_code').upper()
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

        date_api = params.get('receipt_date').split('-')
        date_planned = '{0}-{1}-{2}'.format(
            date_api[2], date_api[1], date_api[0])

        vals = {
            'partner_id': partner_id.id,
            'name': purchase_ref,
            'x_is_interface': True,
            'date_planned': date_planned,
            'po_type_id': po_type_id.id,
        }

        order_line_vals_list = [(0, 0, self._prepare_order_lines(
            order_line))
            for order_line in params.get('lineItems')
        ]
        vals['order_line'] = order_line_vals_list

        purchase = Purchase.new(vals)
        purchase.onchange_partner_id()
        purchase_values = purchase._convert_to_write(purchase._cache)
        purchase_id = Purchase.create(purchase_values)
        purchase_id.button_confirm()

        return purchase_id.name

    @KBTApiBase.api_wrapper(['kbt.purchase_update'])
    @http.route('/purchase/update', type='json', auth='user')
    def purchase_order_update_api(self, **params):
        try:
            msg = self._check_purchase_order_update_values(**params)
            if msg:
                return self._response_api(message=msg)
            res = self._update_purchase_order(**params)
            return self._response_api(isSuccess=True, x_purchase_ref=res)
        except requests.HTTPError as http_err:
            return self._response_api(message=str(http_err))
        except Exception as error:
            return self._response_api(message=str(error))

    def _check_purchase_order_update_values(self, **params):
        msg_list = []
        if params.get('x_bill_date'):
            msg_list.append('Missing x_bill_date')
        if params.get('x_bill_ref'):
            msg_list.append('Missing x_bill_ref')

        return msg_list

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
            if not seq_id:
                raise ValueError(
                    "seq_id not found."
                )
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

        return purchase_ref
