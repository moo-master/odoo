# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_override_customer = fields.Many2one(
        string='Override Customer Name',
        comodel_name='res.partner',
        store=True,
    )
    

# class ext_account_kin(models.Model):
#     _name = 'ext_account_kin.ext_account_kin'
#     _description = 'ext_account_kin.ext_account_kin'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
