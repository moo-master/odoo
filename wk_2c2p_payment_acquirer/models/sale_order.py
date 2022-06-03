# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.onchange('order_line')
    def check_recurring_product(self):
        for rec in self:
            if any((l.product_id.is_recurring_type or l.product_id.recurring_invoice) for l in rec.order_line) and \
                len(rec.order_line or []) > 1:
                raise ValidationError(_("You cannot add product in the cart as the recurring type product is already added and you are trying to add normal product or normal product is already added and you are trying to add recurring type product in the cart. if you want to add the product you can remove the previous product by clicking clear cart button."));