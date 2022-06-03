/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_2c2p_payment_acquirer.website_sale_extend', function (require) {
    'use strict';

    var ajax = require("web.ajax");
    var website_sale = require('website_sale.website_sale');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('website_sale.VariantMixin');
    var wSaleUtils = require('website_sale.utils');
    const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
    require("web.zoomodoo");
    const {extraMenuUpdateCallbacks} = require('website.content.menu');
    const dom = require('web.dom');

    publicWidget.registry.WebsiteSale.include({
        _onClickAdd: function (ev) {
            var self = this;
            var prdId = $('.product_id').val();

            return async function() {
                const data = await ajax.jsonRpc("/check/cart/products", "call", {"prd_id":prdId,});
                if (data){
                    $('#recurringWarning').modal('show');
                    ev.stopPropagation();
                    return
                }else{
                    var def = () => {
                        self.getCartHandlerOptions(ev);
                        return self._handleAdd($(ev.currentTarget).closest('form'));
                    };
                    if ($('.js_add_cart_variants').children().length) {
                        return self._getCombinationInfo(ev).then(() => {
                            return !$(ev.target).closest('.js_product').hasClass("css_not_available") ? def() : Promise.resolve();
                        });
                    }
                    return def();
                }
            }()
            // return result;
        },

    });
 

})