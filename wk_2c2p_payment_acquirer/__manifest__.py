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
	"name"         : "Webkul 2c2p Paymenr Acquirer",
	"summary"      : """Webkul 2c2p Paymenr Acquirer""",
	"category"     : "Tools",
	"version"      : "1.0.0",
	"sequence"     : 1,
	"author"       : "Webkul Software Pvt. Ltd.",
	"website"      : "https://store.webkul.com/Odoo.html",
	"license"      :  "Other proprietary",
	"description"  : """""",
	"price" 	   : 00,
	"currency"     : "",
	"live_test_url": "http://odoodemo.webkul.com/?module=wk_2c2p_payment_acquirer&version=15.0",
	"depends" 	   : ["base", "website_sale","sale_management","sale_subscription"],
	"data"         : [
		# 'views/product_product_views.xml',
		'views/website_template.xml',
		'views/payment_acquirer_views.xml',
		'data/2c2p_payment_acquirer.xml',
	],
	"demo"         : [],
    "assets"       : {
        "web.assets_frontend": [
            "wk_2c2p_payment_acquirer/static/src/js/website_sale.js",
        ],
    },
	"images"       : [],
	"installable"  : True,
	"pre_init_hook": "pre_init_check",
}
