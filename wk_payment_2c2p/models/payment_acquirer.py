# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from hashlib import md5

from odoo import api, fields, models
from odoo.tools.float_utils import float_repr

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'


    provider = fields.Selection(
        selection_add=[('2c2p', '2C2P')], ondelete={'2c2p': 'set default'})
    twoctwop_merchant_id = fields.Char(
        string="2C2P Merchant ID",
        required_if_provider='2c2p')
    twoctwop_secret_key = fields.Char(
        string="2C2P Secret Key", required_if_provider='2c2p',
        groups='base.group_system')



    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != '2c2p':
            return super()._get_default_payment_method_id()
        return self.env.ref('wk_payment_2c2p.payment_method_2c2p').id
