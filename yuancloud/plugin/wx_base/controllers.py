# -*- coding: utf-8 -*-
from yuancloud import http

# class WxBase(http.Controller):
#     @http.route('/wx_base/wx_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_base/wx_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_base.listing', {
#             'root': '/wx_base/wx_base',
#             'objects': http.request.env['wx_base.wx_base'].search([]),
#         })

#     @http.route('/wx_base/wx_base/objects/<model("wx_base.wx_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_base.object', {
#             'object': obj
#         })