# -*- coding: utf-8 -*-
from yuancloud import http

# class WxQrPay(http.Controller):
#     @http.route('/wx_qr_pay/wx_qr_pay/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_qr_pay/wx_qr_pay/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_qr_pay.listing', {
#             'root': '/wx_qr_pay/wx_qr_pay',
#             'objects': http.request.env['wx_qr_pay.wx_qr_pay'].search([]),
#         })

#     @http.route('/wx_qr_pay/wx_qr_pay/objects/<model("wx_qr_pay.wx_qr_pay"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_qr_pay.object', {
#             'object': obj
#         })