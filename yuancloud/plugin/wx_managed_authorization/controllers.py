# -*- coding: utf-8 -*-
from yuancloud import http

# class WxManagedAuthorization(http.Controller):
#     @http.route('/wx_managed_authorization/wx_managed_authorization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_managed_authorization/wx_managed_authorization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_managed_authorization.listing', {
#             'root': '/wx_managed_authorization/wx_managed_authorization',
#             'objects': http.request.env['wx_managed_authorization.wx_managed_authorization'].search([]),
#         })

#     @http.route('/wx_managed_authorization/wx_managed_authorization/objects/<model("wx_managed_authorization.wx_managed_authorization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_managed_authorization.object', {
#             'object': obj
#         })