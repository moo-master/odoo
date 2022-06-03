# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import logging

from werkzeug import urls
import json

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_repr

from odoo.addons.payment import utils as payment_utils
from ..controller.main import TwoCTwoPController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    @api.model
    def _compute_reference(self, provider, prefix=None, separator='-', **kwargs):

        if provider == '2c2p':
            if not prefix:
                prefix = self.sudo()._compute_reference_prefix(
                    provider, separator, **kwargs
                ) or None
            prefix = payment_utils.singularize_reference_prefix(prefix=prefix, separator=separator)
        return super()._compute_reference(provider, prefix=prefix, separator=separator, **kwargs)



    def _get_specific_rendering_values(self, processing_values):

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != '2c2p':
            return res

        api_url = '/payment/2c2p/init'
        _logger.info(self.sale_order_ids)
        sale_order_id = self.sale_order_ids.filtered(lambda s: s.partner_id.id == self.partner_id.id)
        
        user = {
            'user_id' : self.partner_id.id,
            'currency': self.currency_id.name,
            'buyerFullName': self.partner_name,
            'buyerEmail': self.partner_email,
            'buyerPhone': self.partner_phone,
            'countryCode': self.partner_country_id.code,
            'billing': {},
            'shipping': {}
        }
        if sale_order_id:
            billing_add = sale_order_id.partner_invoice_id
            shipping_add = sale_order_id.partner_shipping_id
            if billing_add:
                user['billing'] = {
                    'city': billing_add.city,
                    'state': billing_add.state_id.name,
                    'postalCode': billing_add.zip,
                    'countryCode': billing_add.country_id.code
                },
            if shipping_add:
                user['shipping'] = {
                    'city': shipping_add.city,
                    'state': shipping_add.state_id.name,
                    'postalCode': shipping_add.zip,
                    'countryCode': shipping_add.country_id.code
                },
        twoc2p_values = {
            'user': json.dumps(user),
            'merchantId': self.acquirer_id.twoctwop_merchant_id,
            'secret_key': self.acquirer_id.twoctwop_secret_key,
            'referenceCode': self.reference,
            'description': self.reference,
            'amount': float_repr(processing_values['amount'], self.currency_id.decimal_places or 2),
            'tax': 0,
            'taxReturnBase': 0,
            'currency': self.currency_id.name,
            'buyerFullName': self.partner_name,
            'buyerEmail': self.partner_email,
            'buyerPhone': self.partner_phone,
            'countryCode': self.partner_country_id.code,
            'responseUrl': urls.url_join(self.get_base_url(), TwoCTwoPController._response_url),
            'confirmationUrl': urls.url_join(self.get_base_url(), TwoCTwoPController._confirm_url),
            'api_url': api_url,
        }
        if self.acquirer_id.state != 'enabled':
            twoc2p_values['test'] = 1

        return twoc2p_values


    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != '2c2p':
            return tx

        reference = data.get('invoiceNo')
        if not reference:
            raise ValidationError(
                "2C2P Payment: " + _(
                    "Received data with missing reference (%(ref)s).",
                    ref=reference
                )
            )
        tx = self.search([('reference', '=', reference), ('provider', '=', '2c2p')])
        if not tx:
            raise ValidationError(
                "2C2P Payment: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != '2c2p':
            return

        self.acquirer_reference = data.get('transactionId')

        status = data.get('lapTransactionState')
        state_message = data.get('message')
        if status == 'APPROVED':
            self._set_done(state_message=state_message)
        else:
            _logger.warning(
                "received unrecognized payment state %s for transaction with reference %s",
                status, self.reference
            )
            self._set_error("2C2P Payment Acquirer: " + _(state_message))


    @api.model
    def _handle_feedback_data(self, provider, data):
        tx = super(PaymentTransaction, self)._handle_feedback_data(provider, data)

        data['sale_order'].sudo().write({
                "recurring_unique_id": data.get("recurringUniqueID",""),
                "acquirer_id": tx.acquirer_id.id,
            });
        return tx;