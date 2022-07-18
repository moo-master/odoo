# -*- coding: utf-8 -*-
#################################################################################
# Author: Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
	"name"         : "Webkul 2c2p",
	"summary"      : """Webkul 2c2p""",
	"category"     : "Tools",
	"version"      : "1.0.0",
	"sequence"     : 1,
	"author"       : "Webkul Software Pvt. Ltd.",
	"website"      : "https://store.webkul.com/Odoo.html",
	"license"      :  "Other proprietary",
	"description"  : """""",
	"price" 	   : 00,
	"currency"     : "",
	"live_test_url": "http://odoodemo.webkul.com/?module=wk_payment_2c2p&version=15.0",
	"depends" 	   : ["payment", "portal","wk_2c2p_payment_acquirer"],
	"external_dependencies": {"python": ["jwt"]},
	"data"         : [
		'views/payment_2c2p_template.xml',
		'views/payment_acquirer_views.xml',
		'data/2c2p_payment_acquirer.xml',
	],
	"demo"         : [],
	"images"       : [],
	"installable"  : True,
	"pre_init_hook": "pre_init_check",
	"uninstall_hook": "uninstall_hook",
}
