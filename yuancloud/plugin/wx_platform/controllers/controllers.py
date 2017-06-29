# -*- coding: utf-8 -*-
from yuancloud import http

# class WxPlatform(http.Controller):
#     @http.route('/wx_platform/wx_platform/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_platform/wx_platform/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_platform.listing', {
#             'root': '/wx_platform/wx_platform',
#             'objects': http.request.env['wx_platform.wx_platform'].search([]),
#         })

#     @http.route('/wx_platform/wx_platform/objects/<model("wx_platform.wx_platform"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_platform.object', {
#             'object': obj
#         })