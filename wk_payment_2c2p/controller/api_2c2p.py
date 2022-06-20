# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


import base64
import json
import requests
from .api_2c2p_env import *
import jwt
import logging
import pprint

_logger = logging.getLogger(__name__)

class TwoCTwoPAPI:

    def __init__(self, merchant_id, secret_key, api_root):
        self.data = {};
        self.merchant_id = merchant_id;
        self.secret_key = secret_key;
        self.API_ROOT = MAIN_ROUTE.get(api_root);


    def _get_url(self, path):
        return self.API_ROOT + ENDROUTES.get(path);

    def _generate_sign(self, context):
        return jwt.encode(context, self.secret_key, algorithm="HS256")


    def _validate_sign(self, response):
        context = self._base64_to_json(response)
        original_signature = context['signature']
        context['signature'] = ""
        hashed_signature = self._generate_signature(context)

        return original_signature.lower() == hashed_signature.lower()


    def prepare_payment_token(self, user={}, invoice_no='', desc='', \
        amount=0.0, currency_code='USD', \
        payment_channel=PAYMENTCHANNEL.get("ALL"), \
        user_defined1='', user_defined2='', user_defined3='', \
        user_defined4='', user_defined5='', interest_type='', \
        product_code='', recurring=RECURRING.get("NO"), invoice_prefix='', \
        recurring_amount='', allow_accumulate='', \
        max_accumulate_amt='', recurring_interval='', \
        recurring_count='', charge_next_date='', promotion='', \
        request_3ds=CARDMODE.get("YES"), tokenize_only='', \
        statement_descriptor='',
        frontendReturnUrl=None, backendReturnUrl=None):
        token_request = {
            "merchantID": self.merchant_id,
            "invoiceNo": invoice_no,
            "description": desc,
            "amount": amount,
            "currencyCode": currency_code,
            "frontendReturnUrl": frontendReturnUrl,
            "backendReturnUrl": backendReturnUrl,
            # "paymentChannel": payment_channel,
            "recurring": recurring,
            "recurringAmount": recurring_amount,
            "recurringInterval": recurring_interval,
            "recurringCount": recurring_count,
            "chargeNextDate": charge_next_date,
            "invoicePrefix": invoice_prefix,
            "allowAccumulate": allow_accumulate,
            "maxAccumulateAmount": max_accumulate_amt,
            "uiParams": {
                "userInfo":{
                    "name": user.get("buyerFullName",""),
                    "email": user.get("buyerEmail",""),
                    "countryCode": user.get("countryCode",""),
                    "currencyCode": user.get("currency",""),
                },
            },

        }
        pprint.pformat(token_request)
        return token_request



    def api_call(self, url, data):
        headers = {"Accept": "text/plain", "Content-Type": "application/*+json"}
        payment_request = str(data['signature'])
        _logger.info(jwt.decode(payment_request, self.secret_key, algorithms="HS256"))
        payment_request = "{\"payload\":\"%s\"}"%payment_request
        _logger.info(payment_request)
        
        return requests.post(url, data=payment_request, headers=headers).text

    
    def get_2c2p_token(self, payload):

        url = self._get_url("PAYMENT_TOKEN");

        hash_signature = self._generate_sign(payload)
        payload['signature'] = hash_signature

        response = self.api_call(url, payload)
        try:
            if isinstance(response, str) and response.index('payload'):
                response_dict = jwt.decode(json.loads(response)['payload'], self.secret_key, algorithms="HS256")
                return response_dict
            else:
                return json.loads(response)
        except:
            return json.loads(response)


    def payment_inquiry(self, payload):

        url = self._get_url("PAYMENT_INQUIRY");

        headers = {"Accept": "text/plain", "Content-Type": "application/*+json"}
        payment_request = str(self._generate_sign(payload))
        _logger.info(jwt.decode(payment_request, self.secret_key, algorithms="HS256"))
        payment_request = "{\"payload\":\"%s\"}"%payment_request

        response = requests.post(url, data=payment_request, headers=headers).text

        try:
            if isinstance(response, str) and response.index('payload'):
                response_dict = jwt.decode(json.loads(response)['payload'], self.secret_key, algorithms="HS256")
                return response_dict
            else:
                return json.loads(response)
        except:
            return json.loads(response)


    # def recurring_payment_cancel(self, payload):

    #     url = self._get_url("RECURRING_CANCEL");
    #     print("++|++++++++++", url);

    #     headers = {"Accept": "text/plain", "Content-Type": "application/*+json"}
    #     payment_request = str(self._generate_sign(payload))
    #     print("++|++++++++++", payment_request);
    #     print(jwt.decode(payment_request, self.secret_key, algorithms="HS256"))
    #     payment_request = "{\"payload\":\"%s\"}"%payment_request

    #     response = requests.post(url, data=payment_request, headers=headers).text
    #     print("++|++++++++++", response);
    #     # try:
    #     #     if isinstance(response, str) and response.index('payload'):
    #     #         response_dict = jwt.decode(json.loads(response)['payload'], self.secret_key, algorithms="HS256")
    #     #         return response_dict
    #     #     else:
    #     #         return json.loads(response)
    #     # except:
    #     #     return json.loads(response)