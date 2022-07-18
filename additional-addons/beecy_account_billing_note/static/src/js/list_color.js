odoo.define('beecy_account_billing_note.list_color', function (require) {
    "use strict";
    var ListRenderer = require('web.ListRenderer');
    var DECORATIONS_CUSTOM = [
        'decoration-blood',
    ];
    ListRenderer.include({
        _extractDecorationAttrs: function (node) {
            var decorationsCustom = this._super.apply(this, arguments);
            for (const [key, expr] of Object.entries(node.attrs)) {
                if (DECORATIONS_CUSTOM.includes(key)) {
                    let cssClass;
                    cssClass = key.replace('decoration', 'text');
                    decorationsCustom[cssClass] = py.parse(py.tokenize(expr));
                }
            }
            return decorationsCustom;
        },

    })
})
