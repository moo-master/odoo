# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################
from odoo import api, fields, models, _
from odoo.addons.payment_2c2p.const import Available2c2pCurrency


class AcquirerTo_C_To_P(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('to_c_to_p', '2c2p')], ondelete={'to_c_to_p': 'cascade'})
    to_c_to_p_merchant_id = fields.Char(
        '2c2p Merchant ID', required_if_provider='to_c_to_p', groups='base.group_user')
    to_c_to_p_secret_key = fields.Char(
        '2c2p Secret Key', required_if_provider='to_c_to_p', groups='base.group_user')

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)
        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in Available2c2pCurrency:
            acquirers = acquirers.filtered(lambda a: a.provider != 'to_c_to_p')
        return acquirers

    def _get_to_c_to_p_urls(self):
        if self.state == "enabled":
            url = 'https://t.2c2p.com/RedirectV3/Payment'
        else:
            url = 'https://demo2.2c2p.com/2C2PFrontEnd/RedirectV3/payment'
        return url

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'to_c_to_p':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_2c2p.payment_method_2c2p').id
