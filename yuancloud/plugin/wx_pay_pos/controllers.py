# -*- coding: utf-8 -*-
from yuancloud import http

# class WxPayPos(http.Controller):
#     @http.route('/wx_pay_pos/wx_pay_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_pay_pos/wx_pay_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_pay_pos.listing', {
#             'root': '/wx_pay_pos/wx_pay_pos',
#             'objects': http.request.env['wx_pay_pos.wx_pay_pos'].search([]),
#         })

#     @http.route('/wx_pay_pos/wx_pay_pos/objects/<model("wx_pay_pos.wx_pay_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_pay_pos.object', {
#             'object': obj
#         })