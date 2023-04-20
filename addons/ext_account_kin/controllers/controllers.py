# -*- coding: utf-8 -*-
# from odoo import http


# class ExtAccountKin(http.Controller):
#     @http.route('/ext_account_kin/ext_account_kin', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ext_account_kin/ext_account_kin/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ext_account_kin.listing', {
#             'root': '/ext_account_kin/ext_account_kin',
#             'objects': http.request.env['ext_account_kin.ext_account_kin'].search([]),
#         })

#     @http.route('/ext_account_kin/ext_account_kin/objects/<model("ext_account_kin.ext_account_kin"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ext_account_kin.object', {
#             'object': obj
#         })
