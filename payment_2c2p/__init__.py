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
from . import models
from . import controllers
from odoo.addons.payment import reset_payment_acquirer


def pre_init_check(cr):
    from openerp.service import common
    from openerp.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='15.0':raise Warning('Module support Odoo series 15.0 found {}.'.format(server_serie))
    return True

def uninstall_hook(cr, registry):
    reset_payment_acquirer(cr, registry, 'to_c_to_p')
