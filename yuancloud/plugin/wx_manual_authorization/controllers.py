# -*- coding: utf-8 -*-
from yuancloud import http

# class WxManualAuthorization(http.Controller):
#     @http.route('/wx_manual_authorization/wx_manual_authorization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_manual_authorization/wx_manual_authorization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_manual_authorization.listing', {
#             'root': '/wx_manual_authorization/wx_manual_authorization',
#             'objects': http.request.env['wx_manual_authorization.wx_manual_authorization'].search([]),
#         })

#     @http.route('/wx_manual_authorization/wx_manual_authorization/objects/<model("wx_manual_authorization.wx_manual_authorization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_manual_authorization.object', {
#             'object': obj
#         })