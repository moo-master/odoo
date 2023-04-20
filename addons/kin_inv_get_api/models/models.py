# -*- coding: utf-8 -*-

# from odoo import models, fields, api

# @api.multi
# @api.depends("origin")
# def _compute_invoice_date(self):
#     for invoice in self:
#          invoice_ids = self.env["account.move"].search([("invoice_date","=",invoice.origin)])
#          if len(invoice_ids) >= 0:
#              invoice.invoice_ids = invoice_ids[0]
# invoice_ids = fields.Many2one("sale.order",compute=_compute_invoice_date, store=True) 

