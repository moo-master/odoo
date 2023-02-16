# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


MAIN_ROUTE = {
    "PRODUCTION" : "https://pgw.2c2p.com",
    "SANDBOX" : "https://sandbox-pgw.2c2p.com",
    "PRODUCTION_INDO" : "https://pgwid.2c2p.com",
    "RECURRING_CANCEL_SANDBOX" : "https://demo2.2c2p.com/2C2PFrontend" ,
    "RECURRING_CANCEL" : "https://t.2c2p.com",
}

ENDROUTES = {
    "PAYMENT_TOKEN": "/payment/4.1/PaymentToken",
    "PAYMENT_OPTION": "/payment/4.1/PaymentOption",
    "PAYMENT_OPTION_DETAILS": "/payment/4.1/PaymentOptionDetails",
    "PAYMENT_REQUEST": "/payment/4.1/Payment",
    "PAYMENT_INQUIRY": "/payment/4.1/PaymentInquiry",
    "RECURRING_CANCEL": "/PaymentAction/2.0/action",
}

CARDMODE = {
    "FORCE": "F",
    "YES": "Y",
    "NO": "N",
}

PAYMENTCHANNEL = {
    "ALL": "ALL",
    "CREDIT_CARD": "CC",
    "INSTALLMENT": "IPP",
}

RECURRING = {
    "YES": "Y",
    "NO": "N",
}