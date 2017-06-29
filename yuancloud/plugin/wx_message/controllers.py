# -*- coding: utf-8 -*-
from yuancloud import http

# class WxMessage(http.Controller):
#     @http.route('/wx_message/wx_message/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_message/wx_message/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_message.listing', {
#             'root': '/wx_message/wx_message',
#             'objects': http.request.env['wx_message.wx_message'].search([]),
#         })

#     @http.route('/wx_message/wx_message/objects/<model("wx_message.wx_message"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_message.object', {
#             'object': obj
#         })