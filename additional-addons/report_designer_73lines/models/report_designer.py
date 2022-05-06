# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
import uuid
from odoo import models, fields, api, _
from odoo.addons.website.models.website import slugify
from odoo.exceptions import UserError


class Report(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def new_report(self, name, object_name=False, layout=False):
        templates = self.env['ir.ui.view'].search([('key', 'ilike', 'report_designer_73lines.default_report')], order='id asc')
        layout_templates = self.env['ir.ui.view'].search([('key', 'ilike', layout)], order='id asc')
        report_xmlid = False
        uq_key = str(uuid.uuid4()).replace('-', '')[:8]
        report_name = slugify(name, max_length=50) + "-" + uq_key
        template_module = report_name.replace('-', '_')

        for template in templates:
            report_xmlid = self.env['report.designer'].copy_template_data(template, template_module, report_name, object_name, layout)

        for layout_temp in layout_templates:
            self.env['report.designer'].copy_layout_data(layout_temp, template_module, report_name, object_name, layout)

        self.env['ir.module.module'].create({
            "name": template_module,
            "shortdesc": name,
            "application": False,
            "icon": "/base/static/description/icon.png",
            "description": "Export report using Report Designer",
            "state": "installed",
            "author": self.env.user.company_id.name,
        })
        return report_xmlid


class ReportDesigner(models.Model):
    _name = 'report.designer'
    _description = 'Report Designer Model.'

    @api.model
    def get_record_data(self, report_id=False):
        rec_dict = {}
        if report_id:
            ir_report_model = self.env['ir.actions.report'].browse([int(report_id)])
            records = self.env[ir_report_model.model].search([])
            for record in records:
                rec_dict[record.id] = record.display_name
        return rec_dict

    @api.model
    def get_field_data(self, report_id=False):
        rec_dict = {}
        if report_id:
            ir_report_model = self.env['ir.actions.report'].browse([int(report_id)])
            record = self.env['ir.model'].search([('model', '=', ir_report_model.model)])
            for field in record.field_id:
                rec_dict[field.name] = field.display_name

            return rec_dict

    def copy_layout_data(self, layout_temp, layout_module, report_name, object_name, layout):
        template_name = layout_temp.key.split('.')[1]
        if '_document' in template_name:
            report_name = report_name + '_document'
        report_xmlid = "%s.%s" % (layout_module, report_name)
        template_id = layout_temp
        key = layout_module + '.' + layout_temp.name
        report = template_id.with_context(website_id=False).copy({'key': key, 'is_report_designer_template': True})
        ir_model_data =self.env['ir.model.data'].create({'module': key,
                                          'model': 'ir.ui.view',
                                          'name': report_name,
                                          'res_id': report})
        report.write({
            'name': report_name,
            'model': object_name,
        })
        return report_xmlid


    def copy_template_data(self, template, template_module, report_name, object_name, layout):
        template_name = template.key.split('.')[1]
        if '_document' in template_name:
            report_name = report_name + '_document'
        report_xmlid = "%s.%s" % (template_module, report_name)
        template_id = template
        key = template_module + '.' + report_name
        report = template_id.with_context(website_id=False).copy({'key': key, 'is_report_designer_template': True})
        ir_model_data =self.env['ir.model.data'].create({'module': template_module,
                                          'model': 'ir.ui.view',
                                          'name': report_name,
                                          'res_id': report})
        report_arch = report.arch.replace(template.key, report_xmlid)
        report.write({
            'arch': report_arch.replace('web.external_layout', layout),
            'name': report_name,
            'model': object_name,
        })
        return report_xmlid


class TagAttributeName(models.Model):
    _name = 'tag.attribute.name'
    _description = 'Model For Tag Attribute Name.'

    name = fields.Char(string='Attribute Name', required=True)


class TagAttribute(models.Model):
    _name = 'tag.attribute'
    _description = 'Model For Tag Attribute.'

    name = fields.Many2one('tag.attribute.name', string='First Attribute', required=True)
    is_iterable = fields.Boolean(string='Is Iterable ?')
    is_renderable = fields.Boolean(string='Is Renderable ?')
    is_option = fields.Boolean(string='Is Option ?')
    is_use_with_only_field = fields.Boolean(string='Is Use with only Fields ?')
    priority = fields.Integer(string='Priority', required=True)
    second_attribute = fields.Many2one('tag.attribute.name', string='Second Attribute')
    with_attrs = fields.Many2many('tag.attribute.name', string='Attributes can use with main attribute')

    @api.onchange('name', 'second_attribute')
    def onchange_directives(self):
        if self.name and self.second_attribute and self.name == self.second_attribute:
            raise UserError(_('First and Second Attribute are Same'))


class ReportWidget(models.Model):
    _name = 'report.widget'
    _description = 'Model For Different Widget In Report.'

    name = fields.Char(string='Widget Name', required=True)
    widget_json = fields.Char(string='Widget JSON', required=True)
