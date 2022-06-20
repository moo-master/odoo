# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from ..controller.api_2c2p import TwoCTwoPAPI

class SubscriptionSale(models.Model):
    _inherit = "sale.subscription"


    recurring_unique_id = fields.Char(string="Recurring Unique ID");
    acquirer_id = fields.Many2one("payment.acquirer");


    # def _cron_recurring_create_invoice(self):
    #     res = super(SubscriptionSale, self)._cron_recurring_create_invoice();

    #     if len(res or []) != 0:
    #         obj = self._prepare_api_obj("RECURRING_TEST", "RECURRING");

            



    # def _prepare_api_obj(self, test, main):
    #     return TwoCTwoPAPI(
    #             self.acquirer_id.twoctwop_merchant_id,
    #             self.acquirer_id.twoctwop_secret_key,
    #             test if self.acquirer_id.state == 'test' else main
    #         )

    # def set_close(self):
    #     res = super(SubscriptionSale, self).set_close()

    #     #api call
    #     print("+++++++++++++++++",self.acquirer_id)
    #     obj = self._prepare_api_obj('RECURRING_CANCEL_SANDBOX', 'RECURRING_CANCEL')
    #     print("+++++++++++++++++++++++",obj)
    #     obj.recurring_payment_cancel({
    #             "version": 2.1,
    #             "merchantID": self.acquirer_id.twoctwop_merchant_id,
    #             "recurringUniqueID": self.recurring_unique_id,
    #             "processType": "C",
    #         });
    #     return res;



class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    
    recurring_unique_id = fields.Char(string="Recurring Unique ID");
    acquirer_id = fields.Many2one("payment.acquirer");


    def _prepare_subscription_data(self, template):
        res = super(SaleOrderInherit, self)._prepare_subscription_data(template);

        res.update({
                "recurring_unique_id": self.recurring_unique_id,
                "acquirer_id": self.acquirer_id.id,
            })
        return res;


    # def _action_confirm(self):

    #     res = super(SaleOrderInherit, self)._action_confirm()

    #     subscription = self.order_line.mapped('subscription_id');
    #     if subscription and len(self.recurring_unique_id or ""):
    #          #self._create_invoices();
    #     return res


