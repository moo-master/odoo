# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class kin_technical_access(models.Model):
#     _name = 'kin_technical_access.kin_technical_access'
#     _description = 'kin_technical_access.kin_technical_access'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
