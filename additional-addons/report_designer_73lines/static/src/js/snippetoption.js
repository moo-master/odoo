odoo.define('report_designer_73lines.snippets.options', function (require) {
'use strict';

var options = require('web_editor.snippets.options');
var core = require('web.core');
var QWeb = core.qweb;
var ajax = require('web.ajax');
var rpc = require('web.rpc');
var qs_obj = $.deparam($.param.querystring());
var ModelFieldSelector = require("web.ModelFieldSelector");
var Attributes = null;

options.registry.report_attribute = options.Class.extend({
    init: function(){
        this._super.apply(this, arguments);
        var report_id = qs_obj.report_id;
        var self = this;
        ajax.jsonRpc('/report/get_report_html/', 'call', {
                report_id: report_id,
            }).then(function (res) {
                Attributes = res.attributes;
        });
        var $target_el = this.$target;
        var attribute_obj = {};
        var $tr = $($target_el.closest('[t-foreach]'));
        for (var idx = 0, len = this.$target[0].attributes.length; idx < len; idx++) {
            attribute_obj[this.$target[0].attributes[idx].name] = this.$target[0].attributes[idx].nodeValue
        }
        var isForeach = !("t-foreach" in attribute_obj) && $tr.length && $tr.attr('t-foreach') ? $tr.attr('t-foreach') : null;
        ajax.jsonRpc('/report_designer/dialog', 'call', {
                'report_id': report_id,
                'attribute_obj': attribute_obj,
                'foreach_field': isForeach
            }).then(function (result) {
                self.$el.find(".here_form_render").html(QWeb.render('report_designer_dialogbox', {
                    field_names: result.field_names,
                    function_names: result.function_names,
                    attribute_obj: attribute_obj,
                    relation_field_names: result.relation_field_names,
                    as: isForeach ? $tr.attr('t-as') : null
                })).after(QWeb.render('WidgetGeneratorSelection', {widgets: result.report_widget}));
                self.update_attribute_selection(attribute_obj,self);
                var chain = [];
                if(result.relation_field_names == null){
                    if(attribute_obj.hasOwnProperty('t-field') || attribute_obj.hasOwnProperty('t-foreach')){
                        var fieldObj = attribute_obj['t-field'] || attribute_obj['t-foreach'];
                        chain = fieldObj.toString().split(".");
                        chain.splice(0, 1);
                    }
                }else{
                    if(attribute_obj.hasOwnProperty('t-field')){
                        var fieldObj = attribute_obj['t-field'];
                        chain = fieldObj.toString().split(".");
                        var trFor = $tr.attr('t-foreach').toString().split(".");
                        trFor.splice(0, 1);
                        for(var k=0; k < trFor.length; k++){
                            chain.splice(k, 1, trFor[k]);
                        }
                    }else{
                        var trFor = $tr.attr('t-foreach').toString().split(".");
                        trFor.splice(0, 1);
                        for(var k=0; k < trFor.length; k++){
                            chain.splice(k, 1, trFor[k]);
                        }
                    }
                }

                self.fieldSelector = new ModelFieldSelector(
                    self,
                    result.model,
                    chain.length !== 0 ? chain : ["id"],
                    _.extend({
                        readonly: false,
                    }, options || {})
                );
                self.fieldSelector.appendTo(self.$el.find(".field_selection"));
                var ifChain = [];
                if(attribute_obj['t-if']){
                    ifChain = attribute_obj['t-if'].toString().split(".");
                    ifChain.splice(0, 1);
                }
                self.ifFieldSelector = new ModelFieldSelector(
                    self,
                    result.model,
                    ifChain.length !== 0 ? ifChain : ["id"],
                    _.extend({
                        readonly: false,
                    }, options || {})
                );
                self.ifFieldSelector.appendTo(self.$el.find(".if_field_selection"));
                self.$el.find("#m-fld-normal-m2o, #m-fld-m2m-o2m, #m-rel-fld, #m-fn, #chld-fld").select2();
                self.update_option_color(self.$el,attribute_obj);
                self.$el.find('.field_selection').on('focusout', function (){
                    self._updateFieldSelector(self,attribute_obj, result, $tr);
                });
                self.$el.find('.if_field_selection').on('focusout', function (){
                    var fieldChain = self.ifFieldSelector.chain;
                    if(attribute_obj.hasOwnProperty('t-if')){
                        var fieldChainVal = (attribute_obj['t-if'].toString().split("."))[0];
                        var i = fieldChainVal == 'doc' ? 0 : 1 ;
                    }else{
                        var i = 0;
                        var fieldChainVal = 'doc';
                    }
                    for(i ; i < fieldChain.length; i++){
                        fieldChainVal = fieldChainVal + '.' + fieldChain[i];
                    }
                    self.$el.find("#attribute_value").val(fieldChainVal);
                });
                if(attribute_obj.hasOwnProperty('class')){
                    var allClasses = attribute_obj.class.split(' ');
                    if(allClasses.includes('font-weight-bold')){
                        self.$el.find('#bold_text').addClass('active');
                    }
                    if(allClasses.includes('o_underline')){
                        self.$el.find('#underline_text').addClass('active');
                    }
                    if(allClasses.includes('font-italic')){
                        self.$el.find('#italic_text').addClass('active');
                    }
                }
                self.$el.find("#bold_text, #italic_text, #underline_text").on('click', function (e){
                    self.$target.toggleClass($(this).data('class'));
                    $(e.currentTarget).toggleClass('active');
                    if(self.$target.hasClass('o_underline')){
                        self.$target.css('text-decoration', 'underline');
                    }else{
                        self.$target.css('text-decoration', 'none');
                    }
                    var updateAttr = {};
                    for (var idx = 0, len = $target_el[0].attributes.length; idx < len; idx++) {
                        updateAttr[$target_el[0].attributes[idx].name] = $target_el[0].attributes[idx].nodeValue
                    }
                    self.update_value_fun($target_el,updateAttr);
                });
                self.$el.find("#attribute_type").on('change', function (e) {
                    self.selected_text = $(this).val().trim();
                    self.json_val = Attributes['all'][self.selected_text] ? Attributes['all'][self.selected_text] : null;
                    self.$el.find("#m-fld-normal-m2o, #m-fld-m2m-o2m, #m-rel-fld, #m-fn, #chld-fld, #widget_name").val('').trigger('change.select2');

                    self.$el.find(".attr-1 > .attr-inner, .attr-1 > .c-attr-1-custom-type, .attr-2").addClass('d-none');
                    self.$el.find(".attr-1").removeClass('d-none');

                    $('#m-rel-fld').html('');

                    self.$el.find("#custom_attribute_type, #attribute_value, #second_attribute_type, #second_attribute_value").removeClass('input-attr-value-err');

                    if(Object.keys(Attributes['option']).includes(self.selected_text)){
                        self.$el.find('#report_designer_attribute').addClass('col-sm-8');
                        self.$el.find('#widget-selection').addClass('col-sm-4').removeClass('d-none');
                        var $AppendEl = self.$el.find('.attr-2');
                        self.$el.find('#widget-selection').insertAfter($AppendEl);
                    }else{
                        self.$el.find('#report_designer_attribute').removeClass('col-sm-8');
                        self.$el.find('#widget-selection').removeClass('col-sm-4').addClass('d-none');
                    }
                    self.$el.find(".attr-1, .attr-1 > .attr-inner , .attr-2, .c-m-sel").removeClass('d-none');
                    self.$el.find(".c-m-fld-normal-m2o, .c-m-rel-fld, .c-m-fld-m2m-o2m, .c-m-fn").removeClass('d-none');
                    if(Object.keys(Attributes['normal']).includes(self.selected_text) || Object.keys(Attributes['option']).includes(self.selected_text)){
                        self.$el.find(".attr-1 > .attr-inner, .attr-2").addClass('d-none');
                        self.$el.find(".attr-1").removeClass('d-none');
                    } else if (Object.keys(Attributes['iterable']).includes(self.selected_text)){
                        self.$el.find(".child_object").addClass('d-none');
                        self.$el.find(".c-m-fld-normal-m2o, .c-m-rel-fld").addClass('d-none');
                    } else if (Object.keys(Attributes['use_with_field']).includes(self.selected_text)) {
                        self.$el.find(".c-m-fld-m2m-o2m, .c-m-fn").addClass('d-none');
                        if(isForeach){
                            self.$el.find(".c-m-sel").addClass('d-none');
                        }
                    } else if (!self.selected_text.startsWith('t-')) {
                        self.$el.find(".attr-1 > .attr-inner , .attr-2, .c-m-sel").addClass('d-none');
                        self.$el.find(".c-m-fld-normal-m2o, .c-m-rel-fld, .c-m-fld-m2m-o2m, .c-m-fn").addClass('d-none');
                    }
                    if(self.selected_text == 't-field' || self.selected_text == 't-foreach'){
                        self.$el.find('.field_selection').removeClass('d-none');
                    }else{
                        self.$el.find('.field_selection').addClass('d-none');
                    }
                    if(self.selected_text == 't-if'){
                        self.$el.find('.if_field_selection').removeClass('d-none');
                    }else{
                        self.$el.find('.if_field_selection').addClass('d-none');
                    }
                    if (self.selected_text == "custom") {
                        self.$el.find(".c-attr-1-custom-type").removeClass('d-none');
                        self.$el.find("#custom_attribute_type").val('');
                    }

                    if (self.selected_text in attribute_obj) {
                        self.$el.find("#attribute_value").val(attribute_obj[self.selected_text]);
                        if (attribute_obj[self.selected_text].indexOf('doc.') !== -1) {
                            self.$el.find("#m-fld-normal-m2o, #m-fld-m2m-o2m, #m-fn").val(attribute_obj[self.selected_text]).trigger('change.select2');
                        } else if ($tr.length && attribute_obj[self.selected_text].indexOf($tr.attr('t-as') + '.') !== -1) {
                            self.$el.find("#chld-fld").val(attribute_obj[self.selected_text]).trigger('change.select2');
                        } else {
                            self.$el.find('#m-fld-normal-m2o').val('');
                        }
                        self.update_button(self.selected_text, 'Update', 1);
                    } else {
                        self.$el.find("#attribute_value").val('');
                        self.update_button(self.selected_text, 'Add');
                    }
                    if (self.json_val) {
                        var second_attr = self.$el.find("#second_attribute_type, #second_attribute_value");
                        second_attr.parent().parent().addClass('d-none');
                        second_attr.val('');
                        if (self.json_val.second_attribute) {
                            second_attr.parent().parent().removeClass('d-none');
                            self.$el.find("#second_attribute_type").val(self.json_val.second_attribute);
                            var $s_value = self.$el.find("#second_attribute_value");
                            $s_value.val(self.json_val.second_attribute in attribute_obj ? attribute_obj[self.json_val.second_attribute] : '');
                            if(Object.keys(Attributes['iterable']).includes(self.selected_text) && !$s_value.val()){
                                self.$el.find("#second_attribute_value").val('line');
                            }
                        }
                    }
                    if (self.selected_text) {
                        $('.c-add-remove').removeClass('d-none');
                    } else {
                        $('.attr-1, .attr-1 > .attr-inner, .attr-2, .c-add-remove').addClass('d-none');
                    }
                });

                self.$el.find("#m-fld-normal-m2o, #m-fld-m2m-o2m, #m-fn, #chld-fld, #widget_name").on('change', function (e) {
                    $('#m-rel-fld').html('');
                    self.$el.find("#attribute_value").val($(this).val());
                    if($(this).prop('id') == 'm-fld-normal-m2o'){
                        var field = $(this).val().split('.')[1];
                        var relation_model = result.field_names[field]['relation'];
                        if(relation_model){
                            rpc.query({
                                model: 'ir.model.fields',
                                method: 'search_read',
                                domain: [['model', '=', relation_model]],
                                fields: ['name', 'field_description', 'ttype']
                            }).then(function (relation_fields) {
                                var $rel_selection_html = $(QWeb.render('MainObjectRelationFields', {
                                    fields: relation_fields,
                                    obj: field
                                }));
                                $('#m-rel-fld').html($rel_selection_html);
                            })
                        }
                    }
                });

                self.$el.find("#m-rel-fld").on('change', function (e) {
                    self.$el.find("#attribute_value").val($(this).val());
                });

                self.$el.find("#save_close").on('click', function (e) {
                    if(!self._checkAttrValue(self)){
                        return false;
                    }
                    self.$el.find("#add_update_attr").trigger('click');
                    self.$el.find('.btn-save').trigger('click');
                    self.update_value_fun($target_el,attribute_obj);
                });

                self.$el.find("#add_update_attr").on('click', function (e) {
                    e.preventDefault();
                    if (!self._checkAttrValue(self)) {
                        return false;
                    }
                    var sel_key = self.selected_text == "custom" ? self.$el.find("#custom_attribute_type").val() : self.selected_text;
                    attribute_obj[sel_key] = self.$el.find("#attribute_value").val();
                    if (self.json_val) {
                        if (self.json_val.second_attribute) {
                            attribute_obj[self.$el.find("#second_attribute_type").val()] = self.$el.find("#second_attribute_value").val();
                        }
                    }
                    self.update_attribute_selection(attribute_obj,self);
                    self.update_button(self.selected_text, 'Update', 1);
                    self.update_value_fun($target_el,attribute_obj);
                    self.$el.find("#attribute_type option[value='']").prop('selected', true).trigger('change');
                });

                self.$el.find("#remove_attr").on('click', function (e) {
                    e.preventDefault();
                    delete attribute_obj[self.selected_text];
                    if (self.json_val) {
                        if (self.json_val.second_attribute) {
                            delete attribute_obj[self.$el.find("#second_attribute_type").val()];
                        }
                    }
                    self.update_attribute_selection(attribute_obj,self);
                    self.update_button(self.selected_text, 'Add');
                    self.$el.find("#attribute_type option[value='']").prop('selected', true).trigger('change');
                    self.update_value_fun($target_el,attribute_obj);
                });

                self.$el.find("#attribute_type option[value='t-field']").prop('selected', true).trigger('change');

            });
    },
    update_option_color: function (dialog,attribute_obj) {
        _.each(dialog.find("#attribute_type option"), function (option) {
            option = $(option);
            option.removeAttr('style');
            if (option.text().trim() in attribute_obj) {
                option.css({
                    'color': 'green',
                    'font-weight': 'bold'
                });
            }
        });
    },
    _updateFieldSelector: function(self, attribute_obj, result, $tr){
        var fieldChain = self.fieldSelector.chain;
        if(attribute_obj.hasOwnProperty('t-field')){
            var fieldChainVal = (attribute_obj['t-field'].toString().split("."))[0];
            var i = fieldChainVal == 'doc' ? 0 : 1 ;
        }else{
            var i = 0;
            var fieldChainVal = 'doc';
        }
        if(result.relation_field_names == null){
            for(i ; i < fieldChain.length; i++){
                fieldChainVal = fieldChainVal + '.' + fieldChain[i];
            }
        }else{
            fieldChainVal = $tr.attr('t-as');
            for(i = 1 ; i < fieldChain.length; i++){
                fieldChainVal = fieldChainVal + '.' + fieldChain[i];
            }
        }
        self.$el.find("#attribute_value").val(fieldChainVal);
    },
    update_attribute_selection: function (attribute_obj,self) {
        var NewAttributes = $(this)[0].Attributes;
        var _list = Object.keys(attribute_obj);
        var flag = false, t = [], priority = 10;
        _.each(_list, function (l) {
            if (Attributes['all'][l]) {
                if (priority > Attributes['all'][l].priority){
                    priority = Attributes['all'][l].priority;
                    if (Attributes['all'][l].is_renderable) flag = true;
                    if (Attributes['all'][l].with_attrs.length) {
                        t = Attributes['all'][l].with_attrs;
                    }
                }
            }
        });
        if (!flag) {
            t = Object.keys(Attributes['all']);
        } else {
            t = t.concat(Object.keys(Attributes['normal']));
        }
        t = _.uniq(t.concat(_list));
        t = _.filter(t, function (a) {
            return !Attributes['sec_attrs'].includes(a)
        });
        t.sort();
        this.$el.find("select#attribute_type").html(QWeb.render('AttributeSelection', {attribute_types: t}));
        this.update_option_color(this.$el,attribute_obj);
    },
    update_button: function (selected_text, btn_text, remove_btn) {
        this.$el.find("#remove_attr").prop('disabled', !remove_btn);
        this.$el.find("#add_update_attr").html(btn_text).prop('disabled', !selected_text.length);
    },
    _checkAttrValue:function(self){
        if (!this.selected_text.length) return true;
        var $allFields = null, cnt = 0;
        if (this.selected_text == "custom") {
            $allFields = this.$el.find("#custom_attribute_type, #attribute_value");
            }else if (this.json_val && this.json_val.second_attribute) {
            $allFields = this.$el.find("#attribute_value, #second_attribute_type, #second_attribute_value");
        }else {
            $allFields = this.$el.find("#attribute_value");
        }
        _.each($allFields, function (field) {
            field = $(field);
            if (!field.val().length) {
                field.addClass('input-attr-value-err');
                cnt++;
            }
        });
        if (cnt > 0) {
            alert("Attribute value required");
            return false;
        } else {
            return true;
        }
    },
    update_value_fun:function ($target_el,attribute_obj){
        var self = this;
        if($target_el.attr('t-foreach')){
            var oldAttr = $target_el.attr('t-as');
            var newAttr = attribute_obj['t-as'];
            $target_el.html($target_el.html().split(oldAttr + '.').join(newAttr + '.'));
        }
        $target_el.each(function () {
            var attributes = $.map(this.attributes, function (item) {
                return item.name;
            });
            var tag = $(this);
            $.each(attributes, function (i, item) {
                tag.removeAttr(item);
            });
        });

        for (var key in attribute_obj) {
            $target_el.attr(key, attribute_obj[key]);
        }

        self.trigger_up('request_history_undo_record', {$target: $target_el});
        if ($target_el.attr('t-field')) {
            $target_el.html($target_el.attr('t-field'));
        }
        if ($target_el.attr('t-raw')) {
            $target_el.html($target_el.attr('t-raw'));
        }
        if ($target_el.attr('t-esc')) {
            $target_el.html('<b>Esc: </b>' + $target_el.attr('t-esc'));
        }
        if ($target_el.attr('t-set') && $target_el.attr('t-value')) {
            var span_text = '<b> Set: </b>' + $target_el.attr('t-set') + ' <b> Value: </b>'+ $target_el.attr('t-value');
            $target_el.html(span_text);
        }
    }

    });
});