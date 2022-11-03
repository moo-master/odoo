import requests

from odoo import http
from odoo.http import request
from odoo.addons.kbt_api_base.controllers.main import KBTApiBase

from datetime import datetime


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
        vals = {}

        if not order_line.get('product_code') and order_line.get('note'):
            vals = {
                'sequence': order_line.get('seq_line'),
                'name': order_line.get('note'),
                'display_type': "line_note",
                'product_qty': 0,
            }
        elif order_line.get('product_code'):
            if order_line.get('analytic_account'):
                account_analytic_id = Account.search(
                    [('code', '=', order_line.get('analytic_account'))])
                if not account_analytic_id:
                    raise ValueError(
                        "Analytic Account Code Not Found."
                    )
                vals.update({
                    'account_analytic_id': account_analytic_id.id
                })

            product_id = request.env['product.product'].search([
                ('default_code', '=', order_line.get('product_code')),
            ])
            if not product_id:
                raise ValueError(
                    "product_id not found"
                )

            wht_id = product_id.purchase_wht_type_id
            if 'x_wht_id' in order_line:
                wht_id = request.env['account.wht.type'].search([
                    ('sequence', '=', (seq := int(order_line.get('x_wht_id')))),
                ])
                if not wht_id:
                    raise ValueError(
                        "Withholding Tax: %s have no data." % seq
                    )

            vals.update({
                'product_id': product_id.id,
                'name': order_line.get('name'),
                'qty_received': 0,
                'product_qty': order_line.get('product_uom_qty'),
                'price_unit': order_line.get('price_unit'),
                'sequence': order_line.get('seq_line'),
                'note': order_line.get('note'),
                'wht_type_id': wht_id.id

            })
        else:
            raise ValueError(
                "This item is neither 'product' nor 'note'."
            )

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

        po_type = params.get('x_po_type_code')
        po_type_id = Business.search([
            ('x_code', '=', po_type)
        ])
        if not po_type_id:
            raise ValueError(
                "Business Code: %s have no data." % po_type
            )
        if not po_type_id.is_active:
            raise ValueError(
                f"Business Type Code ({po_type}) is inactive."
            )

        purchase_ref = params.get('x_purchase_ref')
        purchase_ref_id = Purchase.search([
            ('name', '=', purchase_ref)
        ])
        if purchase_ref_id:
            raise ValueError(
                "Purchase %s already exists." % purchase_ref
            )

        date_planned = datetime.strptime(
            params.get('receipt_date'), '%d-%m-%Y')

        vals = {
            'partner_id': partner_id.id,
            'name': purchase_ref,
            'x_is_interface': True,
            'date_planned': date_planned,
            'po_type_id': po_type_id.id,
        }

        self._check_wht_sequence(
            (order_lines := params.get('lineItems')), 'x_wht_id')

        order_line_vals_list = [(0, 0, self._prepare_order_lines(
            order_line))
            for order_line in order_lines
        ]
        vals['order_line'] = order_line_vals_list

        purchase = Purchase.new(vals)
        purchase.onchange_partner_id()
        purchase_values = purchase._convert_to_write(purchase._cache)
        purchase_id = Purchase.create(purchase_values)
        purchase_id.button_confirm()
        purchase_id.write({
            'date_approve': purchase_id.date_approve.replace(
                date_planned.year, date_planned.month, date_planned.day)
        })

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
        return msg_list

    def _update_purchase_order(self, **params):
        Purchase = request.env['purchase.order']
        AccountMove = request.env['account.move']

        purchase_ref = params['x_purchase_ref']
        purchase_ref_id = Purchase.search([
            ('name', '=', purchase_ref),
            ('x_is_interface', '=', True)
        ])
        if not purchase_ref_id:
            raise ValueError("Purchase %s does not exist." % purchase_ref)

        update_line_lst = []
        for order_line in params['lineItems']:
            seq_id = request.env['purchase.order.line'].search([
                ('sequence', '=', order_line.get('seq_line')),
                ('order_id', '=', purchase_ref_id.id)
            ])
            if not seq_id:
                raise ValueError(
                    "seq_id not found. %s" % purchase_ref_id.id
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

        x_bill_date = datetime.strptime(params.get('x_bill_date'), '%d-%m-%Y')\
            if params.get('x_bill_date') else False

        if x_bill_date:
            if purchase_ref_id.date_approve.date() > x_bill_date.date():
                raise ValueError(
                    "Date %s is back date of order date/accounting date." %
                    x_bill_date.strftime('%d-%m-%Y'))

        acc_vals = {
            'ref': params.get('x_bill_ref'),
            'invoice_date': x_bill_date
        }

        purchase_ref_id.write({
            'order_line': update_line_lst
        })
        res = purchase_ref_id.action_create_invoice()

        acc_move = AccountMove.browse([res.get('res_id')])
        acc_move.write(acc_vals)

        return purchase_ref
