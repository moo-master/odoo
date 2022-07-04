# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models, _
from odoo.http import request

class GeoIPRedirectSettings(models.TransientModel):
    
    _name = 'website.guest.checkout'
    _description= 'Website Guest Checkout Conf'

    def execute_settings(self):
        website_id = self.website_id
        enable_guest = self.enable_guest
        website_id.write({
			'enable_guest':enable_guest
			
		})
        return 'ir.act.window.close'

    website_id = fields.Many2one('website',string='Website',required=True)
    enable_guest = fields.Boolean(string='Enable Guest Checkout',related='website_id.enable_guest',readonly=False)