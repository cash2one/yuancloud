# -*- coding: utf-8 -*-
from yuancloud import http

# class WxQr(http.Controller):
#     @http.route('/wx_qr/wx_qr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_qr/wx_qr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_qr.listing', {
#             'root': '/wx_qr/wx_qr',
#             'objects': http.request.env['wx_qr.wx_qr'].search([]),
#         })

#     @http.route('/wx_qr/wx_qr/objects/<model("wx_qr.wx_qr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_qr.object', {
#             'object': obj
#         })