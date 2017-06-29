# -*- coding: utf-8 -*-
from yuancloud import http

# class WxWeblink(http.Controller):
#     @http.route('/wx_weblink/wx_weblink/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_weblink/wx_weblink/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_weblink.listing', {
#             'root': '/wx_weblink/wx_weblink',
#             'objects': http.request.env['wx_weblink.wx_weblink'].search([]),
#         })

#     @http.route('/wx_weblink/wx_weblink/objects/<model("wx_weblink.wx_weblink"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_weblink.object', {
#             'object': obj
#         })