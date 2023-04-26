# -*- coding: utf-8 -*-
# from odoo import http


# class KinTechnicalCustom(http.Controller):
#     @http.route('/kin_technical_custom/kin_technical_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kin_technical_custom/kin_technical_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kin_technical_custom.listing', {
#             'root': '/kin_technical_custom/kin_technical_custom',
#             'objects': http.request.env['kin_technical_custom.kin_technical_custom'].search([]),
#         })

#     @http.route('/kin_technical_custom/kin_technical_custom/objects/<model("kin_technical_custom.kin_technical_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kin_technical_custom.object', {
#             'object': obj
#         })
