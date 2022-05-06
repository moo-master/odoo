# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
import json
import re
import zipfile
from contextlib import closing
import io
import os
from lxml import etree
from lxml.builder import E
import werkzeug
from collections import OrderedDict

from odoo import http, tools
from odoo.http import request

from odoo.addons.web_editor.controllers.main import Web_Editor
from odoo.addons.http_routing.models.ir_http import slugify, unslug


class WebsiteReportDesigner(http.Controller):
    @http.route(['/report/editor'], type='http', auth='user', website=True)
    def select_template(self, **post):
        models = request.env['ir.model'].sudo().search([('transient', '=', False)])
        model_name_lst = []
        for each_model in models:
            model_name_lst.append(each_model.model)
        paperformats = request.env['report.paperformat'].sudo().search([])
        layouts = request.env['ir.ui.view'].sudo().search([('use_as_layout', '=', True)])
        header_layout = request.env['ir.ui.view'].sudo().search(
            [('id', '=', request.env.ref('report_designer_73lines.report_header_external_layout').id)])
        footer_layout = request.env['ir.ui.view'].sudo().search(
            [('id', '=', request.env.ref('report_designer_73lines.report_footer_external_layout').id)])
        no_header_footer_layout = request.env['ir.ui.view'].sudo().search(
            [('id', '=', request.env.ref('report_designer_73lines.report_external_layout_without_header_footer').id)])
        layout_list = [header_layout, footer_layout, no_header_footer_layout]
        for layout_id in layouts:
            layout_list.append(layout_id)
        all_reports = request.env['ir.actions.report'].sudo().search([
            ('model', 'in', model_name_lst),
            ('report_type', 'in', ['qweb-pdf', 'qweb-html']),
            ('is_report_designer', '=', True)],
            order="name asc")

        reports = request.env['ir.actions.report']
        view = request.env['ir.ui.view']
        for report in all_reports:
            domain = report.associated_view()['domain']
            if len(view.search(domain)) > 1:
                reports += report

        values = {
            'models': models,
            'paperformats': paperformats,
            'layouts': layout_list,
            'reports': reports,
        }

        return request.render("report_designer_73lines.main_report_designer_form", values)

    @http.route(['/report_designer/dialog'], type='json', auth='user', website=True)
    def report_designer_dialog(self, **post):
        res = {
            'attribute_types': None,
            'field_names': None,
            'function_names': None,
            'relation_field_names': None,
            'relation_function_names': None,
            'report_widget': None,
            'model': None,
        }
        if post['foreach_field'] and post['foreach_field'].find('doc.', 0, len(post['foreach_field'])) != -1:
            doc, field_name = post['foreach_field'].split('doc.')
            if post['foreach_field'].startswith('doc.', 0, len(post['foreach_field'])):
                report = request.env['ir.actions.report'].sudo().browse(int(post['report_id']))
                if report and report.model and field_name:
                    model_field = request.env['ir.model.fields']._get(report.model, field_name)
                    if model_field.relation:
                        relation_field_names = {}
                        rel_model = request.env[model_field.relation].search([], limit=1)
                        funcs = []
                        for f in dir(rel_model):
                            try:
                                if callable(getattr(rel_model, f)) and not f.startswith("_"):
                                    funcs.append(f)
                            except:
                                pass
                        res['relation_function_names'] = sorted(funcs)
                        all_fields = request.env['ir.model.fields'].search([('model', '=', model_field.relation)])
                        for field in sorted(all_fields):
                            relation_field_names[field.name] = field.field_description
                        sorted(relation_field_names)
                        res['relation_field_names'] = relation_field_names

        field_names = {}
        final_attributes_dict = {}

        for attribute in request.env['tag.attribute'].sudo().search([]):
            final_attributes_dict[attribute.name.name] = json.dumps({
                "name": attribute.name.name,
                "second_attribute": attribute.second_attribute.name or False,
                "with_attrs": ",".join([a.name for a in attribute.with_attrs])
            })

        report_widget = {}
        for widget in request.env['report.widget'].sudo().search([]):
            report_widget[widget.name] = widget.widget_json

        if report_widget:
            res['report_widget'] = report_widget

        report_id = post.get('report_id', False)
        if report_id:
            ir_report_model = request.env['ir.actions.report'].browse([int(report_id)])
            record = request.env['ir.model'].search([('model', '=', ir_report_model.model)])
            model = request.env[ir_report_model.model].search([], limit=1)
            funcs = []
            for f in dir(model):
                try:
                    if callable(getattr(model, f)) and not f.startswith("_"):
                        funcs.append(f)
                except:
                    pass
            res['function_names'] = sorted(funcs)
            for field in sorted(record.field_id):
                field_names[field.name] = {
                    "label": field.field_description,
                    "type": field.ttype,
                    "relation": field.relation
                }
            sorted(field_names)
        res['model'] = request.env['ir.actions.report'].sudo().browse(int(post['report_id'])).model
        res['attribute_types'] = OrderedDict(sorted(final_attributes_dict.items(), key=lambda item: item[1][0]))
        res['field_names'] = field_names

        return res

    @http.route(['/report-designer-snippets'], type='json', auth='user', website=True)
    def designer_templates(self, **post):
        return request.env.ref('report_designer_73lines.report_snippets').render(None)

    @http.route(['/load/snippets'], type='json', auth='user', website=True)
    def load_snippets_templates(self, snippet):
        return request.env['ir.ui.view'].sudo()._render_template(snippet)

    @http.route(['/create-report'], type='http', auth='user', website=True, method=['post'])
    def create_report(self, **post):
        ir_view = request.env['ir.actions.report'].sudo() \
            .new_report(post.get('name'), object_name=post.get('model'), layout=post.get('layout'))
        vals = {
            'name': post.get('name'),
            'model': post.get('model'),
            'type': 'ir.actions.report',
            'report_type': post.get('report_type'),
            'report_name': ir_view,
            'is_report_designer': True
        }

        if post.get('paperformat', False):
            vals.update({'paperformat_id': post.get('paperformat')})

        report = request.env['ir.actions.report'].sudo().create(vals)
        report.create_action()
        url = "/report/edit/" + re.sub(r"^report_designer_73lines\.", '', ir_view) + "?report_id=" + str(report.id)

        return werkzeug.utils.redirect(url)

    @http.route(['/edit-report'], type='http', auth='user', website=True)
    def edit_report(self, **post):
        selected_report = post.get('reports')
        report_obj = request.env['ir.actions.report'].sudo().browse(int(selected_report))
        url = '/report/edit/' + report_obj.report_name + '?report_id=' + selected_report
        return werkzeug.utils.redirect(url)

    @http.route('/report/edit/<string:report>', type='http', auth="user", website=True, cache=300)
    def edit_report_display(self, report, **kwargs):
        values = {'edit_report': True, 'field_edition': True}
        return request.render('report_designer_73lines.report_designer_loader', values)

    def is_integer(self, string):
        try:
            int(string)
            return True
        except Exception:
            pass

    @http.route('/report/get_report_html/', type='json', website=True, auth="user")
    def get_report_html(self, report_id=False):
        if report_id and self.is_integer(report_id):
            ir_report = request.env['ir.actions.report'].search([('id', '=', report_id)])
            if ir_report:
                tag_attributes = {"all": {}, "normal": {}, "option": {}, "renderable": {}, "iterable": {},
                                  "use_with_field": {}, "sec_attrs": []}
                for attribute in request.env['tag.attribute'].sudo().search([]):
                    tmp = {
                            "name": attribute.name.name,
                            "is_renderable": attribute.is_renderable,
                            "is_iterable": attribute.is_iterable,
                            "is_option": attribute.is_iterable,
                            "is_use_with_only_field": attribute.is_use_with_only_field,
                            "priority": attribute.priority,
                            "second_attribute": attribute.second_attribute.name,
                            "with_attrs": [a.name for a in attribute.with_attrs]
                        }
                    if tmp.get('second_attribute', False):
                        tag_attributes['sec_attrs'].append(tmp['second_attribute'])
                    if attribute.is_option:
                        tag_attributes['option'][attribute.name.name] = tmp
                    elif attribute.is_iterable:
                        tag_attributes['iterable'][attribute.name.name] = tmp
                    elif attribute.is_use_with_only_field:
                        tag_attributes['use_with_field'][attribute.name.name] = tmp
                    elif attribute.is_renderable:
                        tag_attributes['renderable'][attribute.name.name] = tmp
                    else:
                        tag_attributes['normal'][attribute.name.name] = tmp
                    tag_attributes['all'][attribute.name.name] = tmp
                views = request.env['ir.ui.view'].search(
                    [('name', 'ilike', ir_report.report_name.split('.')[1]), ('type', '=', 'qweb')])
                if views:
                    view_name = ir_report.report_name + '_document'
                    element, document = request.env['ir.qweb'].get_template(view_name, {})
                    return {
                        'template': etree.tostring(element, encoding='utf-8').decode(),
                        'id': request.env['ir.ui.view'].get_view_id(view_name) or '',
                        'attributes': tag_attributes
                    }
        return False

    @http.route('/report/preview/<string:report>', type='http', auth="user", website=True)
    def report(self, report, report_id=False, record_id=False):
        if report_id and self.is_integer(report_id):
            ir_report = request.env['ir.actions.report'].search([('id', '=', report_id)])
            if ir_report:
                views = request.env['ir.ui.view'].search(
                    [('name', 'ilike', ir_report.report_name.split('.')[1]), ('type', '=', 'qweb')])
                if views:
                    view_name = ir_report.report_name
                    if record_id and self.is_integer(record_id):
                        values = request.env[ir_report.model].search([('id', '=', int(record_id))])
                    else:
                        values = request.env[ir_report.model].search([], limit=1)
                    return request.render(view_name, {"docs": values})
        return request.render('website.404')

    @http.route('/get/report-details', type='json', auth="user", website=True)
    def get_report_detail(self, report_id):
        ir_report = request.env['ir.actions.report'].browse(report_id)
        if ir_report:
            report_name = ir_report.report_name.split('.')[1]
            module_name = report_name.replace('-', '_')
            modules = ["report_designer_73lines"]
            ir_model = request.env['ir.model'].search([('model', '=', ir_report.model)], limit=1)
            if ir_model and ir_model.modules:
                modules += ir_model.modules.split(", ")
            return {
                "name": module_name,
                "modules": modules
            }
        return False

    @http.route('/report/export/<int:report_id>', type='http', auth="user", website=True)
    def report_export(self, report_id=False, **kwargs):
        if report_id:
            content, report_name = self.get_zip_content(report_id, kwargs)
            if content and report_name:
                return request.make_response(content, headers=[
                    (
                    'Content-Disposition', 'customizations.zip;filename=Report-' + report_name + '-Customizations.zip'),
                    ('Content-Type', 'application/zip'),
                    ('Content-Length', len(content))])
        return request.render('website.404')

    def get_zip_content(self, report_id, kwargs):
        ir_report = request.env['ir.actions.report'].browse(report_id)
        if ir_report:
            modules = kwargs.get('modules', '').split(',') if kwargs.get('modules', '') else []
            report_name = original_report_name = ir_report.report_name.split('.')[1]
            module_name = slugify((kwargs.get('name', report_name))).replace('-', '_')
            module_name_string = module_name.replace('_', ' ').title()
            report_name = module_name.replace('_', '-')

            dir_path = {
                "report_template_path": os.path.join("report", module_name + ".xml"),
                "report_action_path": os.path.join("report", "report_action.xml")
            }
            view = request.env['ir.ui.view'].search([
                ('name', 'ilike', ir_report.report_name.split('.')[1]),
                ('type', '=', 'qweb'),
                ('is_report_designer_template', '=', True),
                ('website_id', '=', False)
            ])

            # File: report/report_action.xml
            report_action = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <report
            id="%s"
            string="%s"
            model="%s"
            report_type="%s"
            file="%s"
            name="%s"
            print_report_name="%s"
        />

        <record id="%s" model="ir.actions.report">
            <field name="is_report_designer">True</field>
        </record>
    </data>
</odoo>
''' % (
                "action_report_" + module_name,
                module_name_string,
                ir_report.model,
                ir_report.report_type,
                module_name + "." + report_name,
                module_name + "." + report_name,
                "'%s-%s' % (object.name, object.id)",
                "action_report_" + module_name
            )

            # File: __init__.py
            init = """# -*- coding: utf-8 -*-

from . import model
            """

            # File: __manifest__.py
            manifest = """# -*- coding: utf-8 -*-
{
    'name': %r,
    'version': '12.0.1.0.3',
    'category': 'Report Designer',
    'description': %s,
    'depends': [%s
    ],
    'data': [%s
    ],
    'application': %s
}
""" % (
                module_name_string,
                'u"""\n%s\n"""' % "Export report using Report Designer",
                ''.join("\n        %r," % value for value in modules),
                ''.join("\n        %r," % value for key, value in dir_path.items()),
                False
            )

            # File: model/__init__.py
            model_init = """# -*- coding: utf-8 -*-

from . import ir_action_report
from . import report_designer
            """
            # File: model/ir_action_report.py
            ir_action_report = """# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    is_report_designer = fields.Boolean(string="Report created by Report Designer or not", default=False)

            """
            # File: model/report_designer.py
            report_designer = """# -*- coding: utf-8 -*-

from odoo import models, fields, api


class View(models.Model):
    _inherit = 'ir.ui.view'

    is_report_designer_template = fields.Boolean(string='Is Report Designer Template', default=False)

            """

            init = init.encode('utf-8')
            manifest = manifest.encode('utf-8')
            model_init = model_init.encode('utf-8')
            ir_action_report = ir_action_report.encode('utf-8')
            report_designer = report_designer.encode('utf-8')

            with closing(io.BytesIO()) as buf:
                tools.trans_export(False, [module_name], buf, 'po', request._cr)
                pot = buf.getvalue()

            with closing(io.BytesIO()) as f:
                with zipfile.ZipFile(f, 'w') as archive:
                    data = E.data()
                    for v in view:
                        data.append(etree.fromstring(v.arch_base))
                        ele = data.findall(".//t[@t-name]")
                        if len(ele):
                            t_name = ele[0].attrib['t-name'].split('.')[1].replace(original_report_name, report_name)
                            ele[0].set('id', t_name)
                            ele[0].tag = "template"
                            del ele[0].attrib['t-name']
                        data.append(etree.fromstring('''
    <record id="%s" model="ir.ui.view">
        <field name="model">%s</field>
        <field name="is_report_designer_template" eval="True"/>
    </record>''' % (t_name, ir_report.model)
                                                     )
                                    )
                    ele_call = data.findall(".//t[@t-call]")
                    for e in ele_call:
                        attrib = e.attrib['t-call']
                        if attrib not in ['web.html_container', 'web.external_layout']:
                            t_call = module_name + "." + attrib.split('.')[1].replace(original_report_name, report_name)
                            e.set('t-call', t_call)

                    template_xml = etree.tostring(E.odoo(data), pretty_print=True, encoding='UTF-8',
                                                  xml_declaration=True)
                    archive.writestr(os.path.join(module_name, dir_path['report_template_path']), template_xml)
                    archive.writestr(os.path.join(module_name, dir_path['report_action_path']), report_action)
                    archive.writestr(os.path.join(module_name, 'i18n', module_name + '.pot'), pot)
                    archive.writestr(os.path.join(module_name, '__init__.py'), init)
                    archive.writestr(os.path.join(module_name, '__manifest__.py'), manifest)
                    archive.writestr(os.path.join(module_name, 'model', '__init__.py'), model_init)
                    archive.writestr(os.path.join(module_name, 'model', 'ir_action_report.py'), ir_action_report)
                    archive.writestr(os.path.join(module_name, 'model', 'report_designer.py'), report_designer)

                return f.getvalue(), (module_name_string + "-" + str(ir_report.id)).replace(' ', '-')
        return ()


class Web_Editor(Web_Editor):
    @http.route()
    def get_assets_editor_resources(self, key, get_views=True, get_scss=True, bundles=False, bundles_restriction=[]):
        bundles_rest = bundles_restriction
        views = super(Web_Editor, self) \
            .get_assets_editor_resources(key,
                                         get_views=get_views,
                                         get_scss=get_scss,
                                         bundles=bundles,
                                         bundles_restriction=bundles_rest)
        url = request.httprequest.headers.get('Referer', '')
        if url.find('/report/edit/') != -1:
            extract_report_key = url.split("?")[0].split("/")
            report_key = extract_report_key[len(extract_report_key) - 1] + "_document"
            view = request.env["ir.ui.view"].get_view_data(report_key)
            views['views'].append(view[0])
        return views
