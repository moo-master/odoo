# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class View(models.Model):
    _inherit = 'ir.ui.view'

    use_as_layout = fields.Boolean(string='Use as Layout', default=False)
    is_report_designer_template = fields.Boolean(string='Is Report Designer Template', default=False)

    #@api.multi
    def render(self, values=None, engine='ir.qweb', minimal_qcontext=False):
        if values and values.get('field_edition', False):
            self.env.context = dict(self.env.context, field_edition=True)
        return super(View, self).render(values=values, engine=engine, minimal_qcontext=minimal_qcontext)

    #@api.multi
    def get_view_data(self, view_id):
        if view_id:
            view = self._view_obj(view_id)
            return view.read(['name', 'id', 'key', 'xml_id', 'arch', 'active', 'inherit_id'])
        else:
            return None

    #@api.multi
    def save(self, value, xpath=None):
        if self._context.get('website_id') and self.is_report_designer_template:
            super(View, self).with_context(website_id=False).save(value, xpath=xpath)
        else:
            super(View, self).save(value, xpath=xpath)
