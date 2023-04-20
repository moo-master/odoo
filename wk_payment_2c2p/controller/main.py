# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging
import pprint
import requests
from .api_2c2p import *
import werkzeug
from odoo.exceptions import ValidationError
import jwt
from datetime import date

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)
import jwt
import json


class TwoCTwoPController(http.Controller):
    _response_url = '/payment/twoctwop/feedback'
    _confirm_url = '/payment/twoctwop/confirm'


    @http.route(_response_url, type='json', auth='public', methods=['GET','POST'], csrf=False, save_session=False)
    def twoctwop_form_feedback(self, **post):
        _logger.info("2C2p Feedback================== %s", pprint.pformat(request.httprequest.data))
        try:
            pa = request.env['payment.acquirer'].sudo().search([('provider','=','2c2p')], limit=1);
            bd = request.env['twoctwop.transaction'].sudo().create({
                'response': json.loads(request.httprequest.data or '{}'),
                });
            bd.resp_d = jwt.decode(json.loads(request.httprequest.data or '{}').get('payload', ''), pa.twoctwop_secret_key, algorithms="HS256");
            _logger.info('Repsonse Saved=========%r===========', bd);
        except:
            _logger.info('Error Occurred-----');



    @http.route('/payment/twoctwop/notification', type='json', auth='public', methods=['GET','POST'], csrf=False, save_session=False)
    def twoctwop_form_notification(self, **post):
        _logger.info("2C2P Notification==================== %s", pprint.pformat(request.httprequest.data))
        # try:
        #     pa = request.env['payment.acquirer'].sudo().search([('provider','=','2c2p')], limit=1);
        #     bd = request.env['back.test'].sudo().create({
        #         'response': str(post) + str(request.httprequest.data),
        #         'rep_type' : 'notification',
        #         });
        #     bd.resp_d = jwt.decode(json.loads(request.httprequest.data or '{}').get('payload', ''), pa.twoctwop_secret_key, algorithms="HS256");
        #     _logger.info('Repsonse Saved-----%r------', bd);
        # except:
        #     _logger.info('Error Occurred-----');

    
    @http.route(_confirm_url, type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def twoctwop_form_confirm(self, **post):
        try:
            response = self.obj.payment_inquiry({
                    "paymentToken" : self.payment_token,
                    "merchantID" : self.merchant_id,
                    "invoiceNo" : self.invoice_no,
                })
        except:
            return request.redirect("/shop/cart")

        state_pol = response.get('respCode')
        if state_pol == '0000':
            lapTransactionState = 'APPROVED'
        elif state_pol == '6':
            lapTransactionState = 'DECLINED'
        elif state_pol == '5':
            lapTransactionState = 'EXPIRED'
        else:
            lapTransactionState = f'INVALID state_pol {state_pol}'

        sale_order = request.env["sale.order"].sudo().browse(request.session.get('sale_order_id' or []));

        data = {
            'TX_VALUE': response.get('fxAmount') or response.get('amount'),
            'currency': response.get('fxCurrencyCode') or response.get('currencyCode'),
            'referenceCode': response.get('referenceNo'),
            'transactionId': response.get('tranRef'),
            'transactionState': response.get('respCode'),
            'message': response.get('respDesc'),
            'lapTransactionState': lapTransactionState,
            'invoiceNo': response.get('invoiceNo'),
            'recurringUniqueID': response.get('recurringUniqueID',''),
            'sale_order': sale_order,
        }

        try:
            request.env['payment.transaction'].sudo()._handle_feedback_data('2c2p', data)
        except ValidationError:
            _logger.warning(
                'An error occurred while handling the confirmation from 2C2P with data:\n%s',
                pprint.pformat(data))
        return request.redirect('/payment/status')

    
    @http.route('/payment/2c2p/init', type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def init_2c2p_payment(self, **post):
        _logger.info(post)
        user = {}

        if post.get('user', False):
            user = json.loads(post.get('user', False))
        try:
            amount = float(post.get('amount', 0.0))
        except:
            amount = 0.0
        
        obj = TwoCTwoPAPI(
                post.get('merchantID'),
                post.get('secret_key'),
               'SANDBOX' if post.get('test', False) == '1' else 'PRODUCTION')
        
        self.obj = obj;
        self.merchant_id = post.get('merchantID');
        self.invoice_no = post.get('invoiceNo');
        self.secret_key = post.get('secret_key');

        sub_details = self.get_subscription_details(user_id=user.get('user_id', False));
        
        token = obj.prepare_payment_token(
                    user=user,
                    invoice_no=post.get('invoiceNo'), 
                    amount=amount, 
                    desc=post.get('description'), 
                    currency_code=post.get('currencyCode'),
                    frontendReturnUrl=post.get('confirmationUrl'),
                    backendReturnUrl=post.get('responseUrl'),
                    recurring=True,
                    recurring_amount=sub_details.get("recurring_amount"),
                    recurring_interval=sub_details.get("recurring_interval"),
                    recurring_count=sub_details.get("recurring_count"),
                    charge_next_date= sub_details.get("charge_next_date").strftime('%d%m%Y'),
                    allow_accumulate=True,
                    max_accumulate_amt=sub_details.get("recurring_amount") * (sub_details.get("recurring_count") or 1),
                    invoice_prefix=post.get('invoiceNo'))
        response = obj.get_2c2p_token(token)
        _logger.info(response)

        website_id = request.env['website'].sudo().browse(request.session.get('force_website_id', []));
        redirectUrl = False
        if response.get('respCode') == '0000':
            self.payment_token = response.get('paymentToken');
            redirectUrl = response.get('webPaymentUrl')
            r = requests.get(redirectUrl)
            return werkzeug.utils.redirect(redirectUrl)
        
        message = 'Something went wrong check the error message\n Error: %s'%(response.get('respDesc')),
        return request.redirect('/shop/payment?error2c2p=1&message=%s'%message);



    def get_subscription_details(self, user_id=False):
        sale_order = request.env["sale.order"].sudo().browse(request.session.get('sale_order_id' or []));
        subscription = request.env["sale.subscription"]
        temp_id = sale_order.order_line.mapped('product_id').subscription_template_id;
        recurring_amount = sale_order.order_line.mapped('price_total')[0];
        recurring_rule = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365,}
        recurring_interval = recurring_rule[temp_id.recurring_rule_type] * temp_id.recurring_interval;
        charge_next_date = subscription._get_recurring_next_date(temp_id.recurring_rule_type, temp_id.recurring_interval, date.today(), date.today().day)
        return {
            "recurring_amount": recurring_amount,
            "recurring_interval": recurring_interval,
            "charge_next_date": charge_next_date,
            "recurring_count": temp_id.recurring_rule_count if temp_id.recurring_rule_boundary == 'limited' else 0,
        }



class WebsiteSaleInherit(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        res = super(WebsiteSaleInherit, self)._get_shop_payment_values(order, **kwargs);
        if kwargs.get('error2c2p', False) == '1':
            res['error2c2p'] = '1';
            res['error_msg2c2p'] = kwargs.get('message', '');
        return res;
