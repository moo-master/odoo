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
    var utils = require('web.utils');

    utils.patch(publicWidget.registry.WebsiteSale.prototype, "WebsiteSaleExtend", {

        _onClickAdd: function (ev) {
            var self = this;
            var prdId = $('.product_id').val();
            var prdTempId;
            let $target = $(ev.target);
            console.log($target.parent())
            console.log($target.parent().find(".product_temp_id").val())
            if ($target.parent().hasClass('o_wsale_product_btn')){
                prdTempId = $target.parent().find(".product_temp_id").val();
                console.log($target.parent().find(".product_temp_id").val());
            }else{
                prdTempId = $target.parent().parent().find(".product_temp_id").val();
                console.log($target.parent().parent().find(".product_temp_id").val());
            }
            console.log(prdId,prdTempId)
            console.log($target)
            var clearCart = $(ev.target).data('now-add');

            return async function() {
                if (clearCart){
                    await ajax.jsonRpc("/clear/shop/cart", "call", {});
                }
                const data = await ajax.jsonRpc("/check/cart/products", "call", {"prd_id":prdId, "prd_temp_id":prdTempId,});
                if (data){
                    console.log(data)
                    if (data === "same"){
                        $('.rw_msg').html("Same product is already added in cart.");
                        $('#recurringWarning').find('#add_to_cart').addClass('d-none');
                        $('.recurClearCart').removeClass('d-none'); 
                        $('#recurringWarning').modal('show');

                        if (prdId === undefined && prdTempId){
                            $target.popover({
                                content : "Same product is alread added in cart.",
                                title: 'Warning',
                                placement: 'top',
                            });
                            $target.popover('show');
                            setTimeout(function(){
                                $target.popover('hide');
                            },5000);
                        }
                        console.log($target)
                        ev.stopPropagation();
                        return true;
                    }
                    if (prdId === undefined && prdTempId){
                        console.log($target)
                        $target.popover({
                            content : "You cannot add product in the cart as the recurring type product is already added and you are trying to add normal product or normal product is already added and you are trying to add recurring type product in the cart.",
                            title: 'Warning',
                            placement: 'top',
                        });
                        $target.popover('show');
                        setTimeout(function(){
                            $target.popover('hide');
                        },5000);
                    }
                    $('#recurringWarning').find('#add_to_cart').removeClass('d-none');
                    $('.recurClearCart').addClass('d-none');
                    $('#recurringWarning').modal('show');
                    ev.stopPropagation();
                    return true;
                }else{
                    $('#recurringWarning').find('#add_to_cart').removeClass('d-none');
                    $('.recurClearCart').addClass('d-none');
                    var def = () => {
                        self.getCartHandlerOptions(ev);
                        return self._handleAdd($(ev.currentTarget).closest('form'));
                    };
                    if ($('.js_add_cart_variants').children().length) {
                        return self._getCombinationInfo(ev).then(() => {
                            return !$(ev.target).closest('.js_product').hasClass("css_not_available") ? def() : Promise.resolve();
                        });
                    }
                    $('#recurringWarning').modal('hide');
                    return def();
                }
            }()
        },


        _onChangeCartQuantity: function (ev) {
            let recc = $(ev.target).data('recurr');
            let quantity = parseInt($(ev.target).val() || '0');
            let $input = $(ev.target);
            console.log(quantity)
            $input.popover({
                content : "You can only add 1 recurring product at a time.",
                title: 'Warning',
                placement: 'top',
            });
            if (quantity === 0){
                return this._super.apply(this, arguments);
            }
            if (recc && quantity !== 1){
                ev.stopPropagation();
                $input.popover('show');
                $input.val(1)//.trigger('change');
                setTimeout(function(){
                    $input.popover('hide');
                },5000);
            }else{
                $input.popover('hide');
                return this._super.apply(this, arguments);
            }
        },


        _onChangeAddQuantity: function (ev) {
            let recc = $(".recurr_product").val();
            let quantity = parseInt($(ev.target).val() || '0');
            let $input = $(ev.target);
            $('.form-control.quantity').popover({
                    content : "You can only add 1 recurring product at a time.",
                    title: 'Warning',
                    placement: 'top',
                });
            if (recc && quantity !== 1){
                ev.stopPropagation();
                $('.form-control.quantity').popover('show');
                $input.val(1)//.trigger('change');
                setTimeout(function(){
                    $('.form-control.quantity').popover('hide');
                },5000);
            }else{
                $('.form-control.quantity').popover('hide');
                this._super.apply(this, arguments);
            }
        },

    })
    // publicWidget.registry.WebsiteSale.include({
    //     selector: '.oe_website_sale',
    //     events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
    //         'click #recur_clear_cart': '_onClickClearCartAddPRD',
    //     }),

    //     _onClickClearCartAddPRD: function(ev){
    //         console.log(ev)
    //         ajax.jsonRpc("/clear/shop/cart", "call", {})
    //         .then(function(data){
    //             if (data){
    //                 $("#add_to_cart").click();
    //             }
    //         })
    //     },

    //     _onClickAdd: function (ev) {
    //         var self = this;
    //         var prdId = $('.product_id').val();

    //         return async function() {
    //             const data = await ajax.jsonRpc("/check/cart/products", "call", {"prd_id":prdId,});
    //             console.log(data);
    //             if (data){
    //                 if (data === "same"){
    //                     $('.rw_msg').html("Same product is already added in cart.");
    //                     $('.recurClearCart').attr("href","/shop/cart"); 
    //                     $('.recurClearCart').html("Go To Cart");
    //                     $('#recurringWarning').modal('show');
    //                     ev.stopPropagation();
    //                     return 
    //                 }
    //                 $('#recurringWarning').modal('show');
    //                 ev.stopPropagation();
    //                 return
    //             }else{
    //                 var def = () => {
    //                     self.getCartHandlerOptions(ev);
    //                     return self._handleAdd($(ev.currentTarget).closest('form'));
    //                 };
    //                 if ($('.js_add_cart_variants').children().length) {
    //                     return self._getCombinationInfo(ev).then(() => {
    //                         return !$(ev.target).closest('.js_product').hasClass("css_not_available") ? def() : Promise.resolve();
    //                     });
    //                 }
    //                 return def();
    //             }
    //         }()
    //         // return result;
    //     },

    // });
 
    // console.log(publicWidget.registry.WebsiteSale.prototype.events)
})