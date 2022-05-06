odoo.define('report_designer_73lines.web_settings_dashboard', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    QWeb.add_template('/report_designer_73lines/static/src/xml/website_templates.xml');

    var SettingReportDesigner = Widget.extend({
        template: 'DashboardReportDesigner',
        events: {
            'click .o_start_report_designing': 'on_start_design',
            'click .o_report_list': 'created_report_list',
        },
        init: function () {
            return this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;
            this._rpc({
                model: 'ir.actions.report',
                method: 'search_read',
                domain: [["is_report_designer", "=", true]],
                fields: ['name'],
            }).then(function (res) {
                self.$el.find('.o_web_settings_dashboard_header').html(res.length + " Reports");
            });

            this._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['database.uuid', false],
            }).then(function (dbuuid) {
                var apps = $('.org_logo_with_uuid_name').attr('data-app-name');
                var src = 'https://srv.73lines.com/get-org-logo';
                $('.org_logo_with_uuid_name').attr('src', src + '?dbuuid=' + dbuuid + '&apps=' + apps);
            });

            this._super.apply(this, arguments);
        },
        on_start_design: function (e) {
            this.do_action('report_designer_73lines.action_report_designer');
        },
        created_report_list: function (e) {
            var self = this;
            this._rpc({
                route: "/web/action/load",
                params: {
                    action_id: "base.ir_action_report",
                }
            }).then(function (action) {
                action.display_name = 'Report Created Using Report Designer';
                action.domain = [['is_report_designer', '=', true]];
                self.do_action(action);
            });
        }

    });
    widget_registry.add('setting_report_designer', SettingReportDesigner);
});