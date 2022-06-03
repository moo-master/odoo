odoo.define('wk_payment_2c2p.payment_form_mixin_inherited', require => {
    'use strict';

    const core = require('web.core');
    const Dialog = require('web.Dialog');
    let payment = require('payment.payment_form_mixin');
    let patch = require('web.utils');

    console.log(payment)

    patch.patch(payment, "Payment 2c2p", {
        _processRedirectPayment : (provider, acquirerId, processingValues) => {
            console.log(processingValues);
            // if (provider === '2c2p'){
            //     // return location.href = '/payment/2c2p/check';
            //     // this._super.apply(this, arguments);
            // }else{
                const $redirectForm = $(processingValues.redirect_form_html).attr(
                    'id', 'o_payment_redirect_form'
                );
                $(document.getElementsByTagName('body')[0]).append($redirectForm);
    
                // Submit the form
                $redirectForm.submit();
            // }
        }
    });

    
});