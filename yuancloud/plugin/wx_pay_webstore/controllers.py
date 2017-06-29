# -*- coding: utf-8 -*-
from yuancloud import http

# class WxPayWebstore(http.Controller):
#     @http.route('/wx_pay_webstore/wx_pay_webstore/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_pay_webstore/wx_pay_webstore/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_pay_webstore.listing', {
#             'root': '/wx_pay_webstore/wx_pay_webstore',
#             'objects': http.request.env['wx_pay_webstore.wx_pay_webstore'].search([]),
#         })

#     @http.route('/wx_pay_webstore/wx_pay_webstore/objects/<model("wx_pay_webstore.wx_pay_webstore"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_pay_webstore.object', {
#             'object': obj
#         })