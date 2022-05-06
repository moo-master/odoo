odoo.define('report_designer_73lines.report_editor', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var wUtils = require('website.utils');
    var Editor = require('web_editor.editor');
    var snippet_editor = require('web_editor.snippet.editor');
    var options = require('web_editor.snippets.options');
    var qs_obj = $.deparam($.param.querystring());
    var Attributes = null;

    var _t = core._t;
    var QWeb = core.qweb;

    QWeb.add_template('/report_designer_73lines/static/src/xml/website_templates.xml');

    var dialog = Dialog.extend({
        init: function (parent, name) {
            var self = this;
            this.name = name;
            this.report_id = parent.report_id;
            this._super(parent, {
                title: _.str.sprintf(_t(this.name)),
                size: 'medium',
                buttons: [{
                    text: _t('Export'),
                    classes: 'btn-primary',
                    click: this.onExport,
                }, {
                    text: _t('Cancel'),
                    close: true,
                }],
            });
        },
        start: function () {
            var self = this;
            rpc.query({
                route: "/get/report-details",
                params: {
                    report_id: this.report_id
                }
            }).then(function (res) {
                if (res) {
                    self.$el.html(QWeb.render("ReportExportDialogContent", res));
                    self.$el.find("#modules").select2({val: res.modules});
                }
            });
        },
        onExport: function (e) {
            window.location = '/report/export/'+ this.report_id + this.getQueryString();
            this.close();
        },
        getQueryString: function () {
            var name = this.$el.find('#report-name').val() || "";
            var modules = this.$el.find('#modules').val() || [];
            var str = "?modules=" + modules + "&name=" + name;
            return str;
        }
    });

    var misc = {
        is_report_editor: function () {
            return (window.location.pathname).indexOf('/report/edit/') !== -1 ? true : false;
        },
        is_report_main_page: function () {
            return (window.location.pathname).indexOf('/report/editor') !== -1 ? true : false;
        }
    };

    var ReportEditor = core.Class.extend({
        init: async function () {
            this.report_id = parseInt(qs_obj.report_id) !== NaN ? parseInt(qs_obj.report_id) : false;
            this.record_id = parseInt(qs_obj.record_id) !== NaN ? parseInt(qs_obj.record_id) : false;
            this.debug = ("" + qs_obj.debug).toString().trim() !== '' ? qs_obj.debug : '';
            await this.start();
        },
        start: async function () {
            await this.on_show()
            $(window).on("load .o_menu_systray", _.bind(this.on_show, this));
            this.load_report();
        },
        load_report: async function () {
            var self = this;
            ajax.jsonRpc('/report/get_report_html/', 'call', {
                report_id: this.report_id,
            }).then(function (res) {
                Attributes = res.attributes;
                if (res) {
                    var $inner_content = $(res.template).html();
                    var $content = $('<div/>')
                        .attr({
                            'class': 'main_page',
                            'data-oe-id': res.id,
                            'data-oe-xpath':".",
                            'data-oe-field':"arch" ,
                            'data-oe-model':"ir.ui.view"
                        })
                        .html($inner_content);
                    $('main').html($content);
                    _.each($('[t-field]'), function (span) {
                        span = $(span);
                        var span_text = span.attr('t-field');
                        span.html(span_text);
                    });
                    _.each($('[t-raw]'), function (span) {
                        span = $(span);
                        var span_text = span.attr('t-raw');
                        span.html(span_text);
                    });
                    _.each($('[t-esc]'), function (span) {
                        span = $(span);
                        var span_text = '<b> Esc: </b>' + span.attr('t-esc');
                        span.html(span_text);
                    });
                    _.each($('[t-set][t-value]'), function (span) {
                        span = $(span);
                        var span_text = '<b> Set: </b>' + span.attr('t-set') + ' <b> Value: </b>'+ span.attr('t-value');
                        span.html(span_text);
                    });
                    $('.report_loader').hide();
                }else{
                    window.location = '/report/editor';
                }
            });
        },
        on_show: async function () {
            var self = this;
            $('header').hide();
            $('footer').hide();
            $('div.navbar').remove();
            $('div#footer').remove();

            $('#report-customize-menu .dropdown-item').on('click', function (e) {
                var id = $(e.currentTarget).attr('id');
                if (id !== 'html_editor') {
                    e.stopPropagation();
                }
            });

            /* Remove Process in navbar */
            var checkExist = setInterval(function () {
                if ($('.o_planner_systray').length) {
                    $('.o_planner_systray').hide();
                    clearInterval(checkExist);
                }
            }, 100);

            /* remove unnecessary menu */
            _.each($('ul.o_menu_systray').children(), function (elem) {
                elem = $(elem);
                var data_action = ("" + elem.find('a[data-action]').attr('data-action')).toString().trim();
                var class_name = ("" + elem.attr('class')).toString().trim();
                if (data_action === 'edit' || class_name.indexOf('report_customize_menu') !== -1) {
                    return;
                } else {
                    elem.remove();
                }
            });

            /* Preview Button Click Event */
            $('a#report_preview').click(function (e) {
                var url = window.location.href.replace('/edit/', '/preview/');
                window.open(url, '_blank');
            });

            /* Export Button Click Event */
            $('a#report_export').click(function (e) {
                new dialog(self, "Export Report").open();
            });

            /* Fill Report Record in selection box */
            rpc.query({
                model: 'report.designer',
                method: 'get_record_data',
                args: [this.report_id],
            }).then(function (data) {
                var option_text = '<option selected="true" disabled="disabled"><b> Select Report Record </b></option>';
                for (var r in data) {
                    if (self.record_id == parseInt(r)) {
                        option_text += '<option value="' + window.location.pathname + '?report_id=' + self.report_id + '&record_id=' + r + '" selected>' + data[r] + '</option>'
                    } else {
                        option_text += '<option value="' + window.location.pathname + '?report_id=' + self.report_id + '&record_id=' + r + '">' + data[r] + '</option>'
                    }
                }
                $('select#all_records').html(option_text).select2();
            }).then(function () {
                $('select#all_records').change(function () {
                    var href = $(this).val();
                    if (core.debug) {
                        href += "&debug=" + self.debug;
                    }
                    href = href.replace('/edit/', '/preview/')
                    window.open(href, '_blank');
                });
            });

            /* Fill Field Generator Record in selection box and Change Event */
            rpc.query({
                model: 'report.designer',
                method: 'get_field_data',
                args: [this.report_id],
            }).then(function (data) {
                var option_text = '<option selected="true" disabled="disabled"><b> Select Report Field </b></option>';
                for (var r in data) {
                    option_text += '<option value="' + r + '">' + data[r] + '</option>'
                }
                $('select#report_field_name').html(option_text);
            }).then(function () {
                $('select#report_field_name').on('change', function (e) {
                    $("input#report_field_generator").val('t-field="doc.' + $(this).val());
                });
            });
            var templates = $('#wrapwrap t[class*="template"]');
            templates.each(function (o, elt) {
                self.replaceTagName(elt);
            });
        },
        replaceTagName: async function (elt) {
            var self = this;
            var newElt = $("<fieldset></fieldset>");
            Array.prototype.slice.call(elt.attributes).forEach(function (a) {
                newElt.attr(a.name, a.value);
            });
            var $legend = $('<legend>&lt; Template &gt;</legend>').css({
                'display': 'block',
                'font-weight': 'bold',
                'font-size': '12px',
                'margin': 0
            }).attr({
               'class': 'placeholder',
                'contenteditable': 'false'
            });
            $(elt).wrapInner(newElt).children(0).unwrap().append($legend);
            var tags = $(elt).find('t[class*="template"]');
            if (tags.length) {
                tags.each(function (o, elt) {
                    self.replaceTagName(elt);
                });
            }
        }
    });

    if (misc.is_report_editor()) {
        new ReportEditor();
    }
    if (misc.is_report_main_page()) {
        $(document).ready(function (e) {
            $('select#model').select2();
        });
    }

    snippet_editor.Class.include({
        events :  _.extend({}, snippet_editor.Class.prototype.events,{
        'click .scroll-link':'_onScrollLink'
        }),
        loadSnippets: function (invalidateCache) {
            if (!invalidateCache && this.cacheSnippetTemplate[this.options.snippets]) {
            this._defLoadSnippets = this.cacheSnippetTemplate[this.options.snippets];
                return this._defLoadSnippets;
            }
            if (misc.is_report_editor()) {
                this.options.snippets = 'report_designer_73lines.report_snippets'
            }
            this._defLoadSnippets = this._rpc({
                model: 'ir.ui.view',
                method: 'render_public_asset',
                args: [this.options.snippets, {}],
                kwargs: {
                    context: this.options.context,
                },
            });
            this.cacheSnippetTemplate[this.options.snippets] = this._defLoadSnippets;
            return this._defLoadSnippets;
        },
        _onScrollLink: function(e){
            this.$el.find('#o_scroll').removeClass('d-none');
            this.$el.find('.o_we_customize_panel').addClass('d-none');
        },
    });

    Editor.Class.include({
        save: function (reload) {
            var self = this;
            if (qs_obj.report_id && misc.is_report_editor()) {
                $('span[t-field], p[t-field], [t-esc], [t-set][t-value],[t-raw]').html('');
                var tags = $('#wrapwrap fieldset[class*="template"]');
                tags.each(function (o, elt) {
                    self.replaceTagName(elt);
                });
                $('#wrapwrap legend[class*="placeholder"]').remove();
            }
            try {
                return this._super.apply(this, arguments);
            } catch (ex) {
                window.location = window.location.href;
            }
        },
        replaceTagName: function (elt) {
            var self = this;
            var newElt = $("<t/>");
            Array.prototype.slice.call(elt.attributes).forEach(function (a) {
                newElt.attr(a.name, a.value);
            });
            $(elt).wrapInner(newElt).children(0).unwrap();
            var tags = $(elt).find('fieldset[class*="template"]');
            if (tags.length) {
                tags.each(function (o, elt) {
                    self.replaceTagName(elt);
                });
            }
        }
    });

    snippet_editor.Editor.include({
        xmlDependencies: [
        '/report_designer_73lines/static/src/xml/website_templates.xml',
        '/web_editor/static/src/xml/snippets.xml'],
        init: function (BuildingBlock, dom) {
            this._super.apply(this, arguments);
            if (qs_obj.report_id && misc.is_report_editor()) {
                if(("" + this.$target.attr('class')).indexOf('main_page') === -1) {
                    $('a#oe_snippet_attribute').removeClass("d-none");
                    $('a#oe_snippet_remove_tr').removeClass("d-none");
                    $('a#oe_snippet_add_tr').removeClass("d-none");
                }
            }
        },
        _onParentClick:function(event){
            event.stopPropagation();
            this.trigger_up('go_to_parent', {$snippet: this.$target});
        },
        _initializeOptions: function () {
            if (qs_obj.report_id && misc.is_report_editor()) {
                this._customize$Elements = [];
                this.styles = {};
                this.selectorSiblings = [];
                this.selectorChildren = [];

                var $element = this.$target;
                while ($element.length) {
                    var parentEditor = $element.data('snippet-editor');
                    if (parentEditor) {
                        this._customize$Elements = this._customize$Elements
                            .concat(parentEditor._customize$Elements);
                        break;
                    }
                    //$element = $element.parent();
                }

                var $optionsSection = $(core.qweb.render('report_designer_customize_block_options_section', {
                    name: this.getName(),
                })).data('editor', this);
                const $optionsSectionBtnGroup = $optionsSection.find('we-top-button-group');
                $optionsSectionBtnGroup.contents().each((i, node) => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        node.parentNode.removeChild(node);
                    }
                });
                $optionsSection.on('mouseenter', this._onOptionsSectionMouseEnter.bind(this));
                $optionsSection.on('mouseleave', this._onOptionsSectionMouseLeave.bind(this));
                $optionsSection.on('click', 'we-title > span', this._onOptionsSectionClick.bind(this));
                $optionsSection.on('click', '.oe_snippet_clone', this._onCloneClick.bind(this));
                $optionsSection.on('click', '.oe_snippet_remove', this._onRemoveClick.bind(this));
                $optionsSection.on('click', '.oe_snippet_parent', this._onParentClick.bind(this));
                this._customize$Elements.push($optionsSection);

                // TODO get rid of this when possible (made as a fix to support old
                // theme options)
                this.$el.data('$optionsSection', $optionsSection);

                var i = 0;
                var defs = _.map(this.templateOptions, val => {
                    if (!val.selector.is(this.$target)) {
                        return;
                    }
                    if (val['drop-near']) {
                        this.selectorSiblings.push(val['drop-near']);
                    }
                    if (val['drop-in']) {
                        this.selectorChildren.push(val['drop-in']);
                    }

                    var optionName = val.option;
                    var option = new (options.registry[optionName] || options.Class)(
                        this,
                        val.$el.children(),
                        val.base_target ? this.$target.find(val.base_target).eq(0) : this.$target,
                        this.$el,
                        _.extend({
                            optionName: optionName,
                            snippetName: this.getName(),
                        }, val.data),
                        this.options
                    );
                    var key = optionName || _.uniqueId('option');
                    if (this.styles[key]) {
                        // If two snippet options use the same option name (and so use
                        // the same JS option), store the subsequent ones with a unique
                        // ID (TODO improve)
                        key = _.uniqueId(key);
                    }
                    this.styles[key] = option;
                    option.__order = i++;

                    if (option.forceNoDeleteButton) {
                        this.$el.add($optionsSection).find('.oe_snippet_remove').addClass('d-none');
                    }

                    return option.appendTo(document.createDocumentFragment());
                });
                if(("" + this.$target.attr('class')).indexOf('main_page') === -1 && ("" + this.$target.attr('class')).indexOf('oe_structure') === -1) {
                    this.$el.find('.oe_snippet_move, .oe_snippet_clone, .oe_snippet_remove').removeClass('d-none');
                } else {
                    this.$el.find('.oe_snippet_move, .oe_snippet_clone, .oe_snipp et_remove').addClass('d-none');
                }

                this.isTargetMovable = (this.selectorSiblings.length > 0 || this.selectorChildren.length > 0);

                this.$el.find('[data-toggle="dropdown"]').dropdown();

                return Promise.all(defs).then(() => {
                    const options = _.sortBy(this.styles, '__order');
                    options.forEach(option => {
                        if (option.isTopOption) {
                            $optionsSectionBtnGroup.prepend(option.$el);
                        } else {
                            $optionsSection.append(option.$el);
                        }
                    });
                    $optionsSection.toggleClass('d-none', options.length === 0);
                });


            }else{
                var defs = [this._super.apply(this, arguments)];
                return Promise.all(defs);
            }
        },
    });
});
