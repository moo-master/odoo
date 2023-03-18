# -*- coding: utf-8 -*-
# from odoo import http


# class KinTechnicalAccess(http.Controller):
#     @http.route('/kin_technical_access/kin_technical_access', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kin_technical_access/kin_technical_access/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kin_technical_access.listing', {
#             'root': '/kin_technical_access/kin_technical_access',
#             'objects': http.request.env['kin_technical_access.kin_technical_access'].search([]),
#         })

#     @http.route('/kin_technical_access/kin_technical_access/objects/<model("kin_technical_access.kin_technical_access"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kin_technical_access.object', {
#             'object': obj
#         })
