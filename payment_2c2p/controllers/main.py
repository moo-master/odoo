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
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class To_C_To_PController(http.Controller):
    _notify_url = '/payment/2c2p/notify/'
    _return_url = '/payment/2c2p/return/'

    @http.route(_notify_url, type='http', auth='public', methods=['POST'], csrf=False)
    def to_c_to_p_notify(self, **post):
        """ to_c_to_p Notify. """
        _logger.info('Beginning 2c2p notify form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo()._handle_feedback_data('to_c_to_p', post)
        return ''

    @http.route(_return_url, type='http', auth="public", methods=['POST', 'GET'], csrf=False, website=True)
    def to_c_to_p_return(self, **post):
        """ to_c_to_p return """
        _logger.info('Beginning 2c2p return response form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo()._handle_feedback_data('to_c_to_p', post)
        return request.redirect('/payment/status')
