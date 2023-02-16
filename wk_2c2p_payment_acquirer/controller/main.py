# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from math import prod
from odoo import addons, fields
from odoo import http, tools, _
import odoo.http as http
from odoo.http import request
import base64	
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.misc import formatLang, get_lang


class WebsiteSaleInherit(WebsiteSale):

    @http.route(["/check/cart/products"], type="json", auth="public", website=True)
    def check_cart_products(self, prd_id=None, prd_temp_id=None):
        try:
            product_id = int(prd_id);
        except:
            product_id = [];
        try:
            product_temp_id = int(prd_temp_id);
        except:
            product_temp_id = [];
        if product_id:
            product = request.env['product.product'].sudo().browse(product_id);
        else:
            product = request.env['product.template'].sudo().browse(product_temp_id);

        sale_order = request.website.sale_get_order(force_create=False);
        if product and (product.recurring_invoice):
            if not sale_order:
                return False;
            if sale_order and not sale_order.order_line:
                return False;
            if sale_order and len(sale_order.order_line or []) == 1:
                if sale_order.order_line.product_id.id == product.id or\
                 sale_order.order_line.product_id.product_tmpl_id.id == product.id:
                    return "same";
                # return True;
            if sale_order and len(sale_order.order_line or []) != 0:
                return True;
        if product and not (product.recurring_invoice):
            if sale_order and any((l.product_id.recurring_invoice) for l in sale_order.order_line):
                return True;
        if sale_order and any((l.product_id.recurring_invoice) for l in sale_order.order_line):
            return True;
        return False;
    


    @http.route(['/clear/shop/cart'],type="json", auth="public", website=True)
    def clear_shop_cart(self, **kw):
        sale_order = request.website.sale_get_order();
        for line in sale_order.order_line:
            line.sudo().unlink();
        return True;


    
    def _get_shop_payment_values(self, order, **kwargs):
        result = super(WebsiteSaleInherit, self)._get_shop_payment_values(order, **kwargs);
        acquirers = result['acquirers'];
        if order and any((l.product_id.recurring_invoice) for l in order.order_line):
            acquirers = result['acquirers'].filtered(lambda a: a.recurring_type == True);
            result['acquirers'] = acquirers;
        else:
            acquirers = result['acquirers'].filtered(lambda a: a.recurring_type == False);
            result['acquirers'] = acquirers;
        return result;