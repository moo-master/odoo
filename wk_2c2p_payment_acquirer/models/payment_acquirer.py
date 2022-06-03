# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import api, fields, models, _

class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"


    recurring_type = fields.Boolean(string="Recurring Type");
