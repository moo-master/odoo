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
import logging
from werkzeug import urls
import hmac
import hashlib

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_2c2p.controllers.main import To_C_To_PController
from odoo.addons.payment_2c2p.const import Available2c2pCurrency

_logger = logging.getLogger(__name__)


class TxTo_C_To_P(models.Model):
    _inherit = 'payment.transaction'

    to_c_to_p_txn_response = fields.Char('2c2p Transaction Response')
    to_c_to_p_payment_channel = fields.Selection([("001", "Credit and debit cards"), ("002", "Cash payment channel"), (
        "003", "Direct Debit"), ("004", "Others"), ("005", "IPP transaction")], '2c2p Payment Channel')

    @staticmethod
    def get_12_char_amount_for_2c2p(amount):
        return str(format(amount, '.2f')).replace(".", "").rjust(12, '0')

    @staticmethod
    def get_HMACSHA1_has_value(data, keys, secretKey):
        res = ''
        if data and secretKey:
            for k in keys:
                res += data.get(k, '')
            hmac_data = hmac.new(str(secretKey).encode(), str(
                res).encode('UTF-8'), hashlib.sha1)
            res = hmac_data.hexdigest()
        return res

    def to_c_to_p_get_form_action_url(self):
        return self._get_to_c_to_p_urls(self.state)['to_c_to_p_form_url']

    def _generate_form_values(self, acquirer):
        vals = dict()

        # Added By Webkul Start
        sale_order_id = self.sale_order_ids.filtered(lambda s: s.partner_id.id == self.partner_id.id)
        base_url = self.get_base_url()
        if sale_order_id.website_id.id and sale_order_id.website_id.domain:
            domain = sale_order_id.website_id.domain
            if not 'http' in domain:
                if 'https' in base_url:
                    base_url = '%s://%s'%('https', domain)
                elif 'http' in domain:
                    base_url = '%s://%s'%('http', domain)
            else:
                base_url = domain
        # Added By Webkul End
        
        # base_url = self.get_base_url()
        currency_id = self.currency_id.name
        vals['data'] = vals['version'] = "6.9"
        vals['reference'] = vals['invoice_no'] = self.reference
        vals['odoo_currency'] = vals['user_defined_5'] = currency_id
        vals['merchant_id'] = acquirer.to_c_to_p_merchant_id
        vals['payment_description'] = f"Payment for: {vals['reference']}"
        vals['order_id'] = self.reference
        vals['amount'] = self.get_12_char_amount_for_2c2p(self.amount)
        vals['currency'] = Available2c2pCurrency.get(currency_id, (''))[0]
        vals['user_defined_1'] = f"{self.partner_id.id}"
        vals['user_defined_2'] = self.partner_name
        vals['user_defined_3'] = self.partner_email
        vals['user_defined_4'] = self.partner_phone
        vals['result_url_1'] = urls.url_join(base_url, To_C_To_PController._return_url)
        vals['result_url_2'] = urls.url_join(base_url, To_C_To_PController._notify_url)
        vals['tx_url'] = acquirer._get_to_c_to_p_urls()
        keys = ('version','merchant_id', 'payment_description', 'order_id', 'invoice_no', 'currency', 'amount', 'user_defined_1', 'user_defined_2', 'user_defined_3', 'user_defined_4', 'user_defined_5', 'result_url_1', 'result_url_2')
        vals['hash_value'] = self.get_HMACSHA1_has_value(vals, keys, acquirer.to_c_to_p_secret_key)
        return vals

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'to_c_to_p':
            return res
        acquirer = self.acquirer_id
        tx_values = self._generate_form_values(acquirer)
        return tx_values

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'to_c_to_p':
            return tx

        reference, hash_value = data.get('order_id'), data.get('hash_value')
        if not reference and not hash_value:
            raise ValidationError(
                "2c2p: " + _(
                    "Received data with missing reference (%(ref)s) or hash_value (%(hash)s)",
                    ref=reference, hash=hash_value,
                )
            )
        tx = self.search([('reference', '=', reference), ('provider', '=', provider)])
        if not tx:
            raise ValidationError(
                "2c2p: " + _("No transaction found matching reference %s.", reference)
            )

        keys = fields = ('version', 'request_timestamp', 'merchant_id', 'order_id', 'invoice_no', 'currency', 'amount', 'transaction_ref', 'approval_code', 'eci', 'transaction_datetime', 'payment_channel', 'payment_status', 'channel_response_code', 'channel_response_desc', 'masked_pan', 'stored_card_unique_id', 'backend_invoice', 'paid_channel', 'paid_agent', 'recurring_unique_id', 'user_defined_1', 'user_defined_2', 'user_defined_3', 'user_defined_4', 'user_defined_5', 'browser_info', 'ippPeriod', 'ippInterestType', 'ippInterestRate', 'ippMerchantAbsorbRate')
        validate_hash = self.get_HMACSHA1_has_value(data, keys, tx.acquirer_id.to_c_to_p_secret_key).upper()
        if validate_hash != hash_value:
            raise ValidationError(
                "2c2p: " + _(
                    "Invalid Hash Value: received %(sign)s, computed %(computed)s.",
                    sign=hash_value, computed=validate_hash
                )
            )
        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'to_c_to_p':
            return
        
        status = data.get('payment_status')
        vals = {
            'acquirer_reference': data.get('transaction_ref'),
            'to_c_to_p_payment_channel': data.get('payment_channel'),
            "to_c_to_p_txn_response": data,
        }
        state_message = ""
        if status == "000":
            state_message = _('Ok: %s') % data.get('channel_response_desc')
            self._set_done()
        elif status == "001":
            state_message = _('Error: %s') % data.get('channel_response_desc')
            self._set_pending()
        elif status == "003":
            state_message = _('Cancel: %s') % data.get('channel_response_desc')
            self._set_canceled()
        else:
            state_message = _('2P2C: feedback error: %s') % data.get('channel_response_desc')
            self._set_error(state_message)
            _logger.warning(state_message)

        if state_message:
            vals['state_message'] = state_message
        self.write(vals)

