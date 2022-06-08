import requests

from odoo import http
from odoo.http import request


class PurchaseController(http.Controller):

    @http.route('/purchase/create', type='json', auth='user')
    def purchase_order_create_api(self, **params):
        try:
            self._create_purchase_order(**params)
        except requests.HTTPError as http_err:
            return {
                'HTTP error': http_err,
            }
        except Exception as error:
            return {
                'error': error,
            }

    def _prepare_order_line(self, order_line, account_analytic_id, po_type):
        product_id = request.env['product.product'].search([
            ('default_code', '=', order_line.get('product_code')),
            ('name', '=', order_line.get('name'))
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
        qty_received = 0
        if po_type in ['K-RENT', 'K-MATCH']:
            qty_received = order_line.get('product_uom_qty')

        wht_seq = order_line.get('x_wht_id')
        wht_id = request.env['account.wht.type'].search([
            ('sequence', '=', wht_seq),
        ])

        if order_line.get('x_wht_id') and not wht_id:
            raise ValueError(
                "Withholding Tax: %s have no data." % wht_seq
            )

        return {
            'account_analytic_id': account_analytic_id.id,
            'product_id': product_id.id,
            'name': order_line.get('name'),
            'qty_received': qty_received,
            'product_qty': order_line.get('product_uom_qty'),
            'price_unit': order_line.get('product_price'),
            'sequence': order_line.get('seq_line'),
            'x_wht_id': wht_id.id or False,
        }

    def _create_purchase_order(self, **params):
        Purchase = request.env['purchase.order']
        Partner = request.env['res.partner']
        Account = request.env['account.analytic.account']
        Business = request.env['business.type']

        partner_ref = params.get('partner_id.ref')
        partner_id = Partner.search(
            [('external_interface_id', '=', partner_ref)])

        if not partner_id:
            partner_id = Partner.create({
                'external_interface_id': partner_ref
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
        if po_type in ['K-RENT', 'K-MATCH']:
            purchase_id.action_create_invoice()
