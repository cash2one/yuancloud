# -*- coding: utf-8 -*-
from yuancloud import http

# class WxMembership(http.Controller):
#     @http.route('/wx_membership/wx_membership/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wx_membership/wx_membership/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wx_membership.listing', {
#             'root': '/wx_membership/wx_membership',
#             'objects': http.request.env['wx_membership.wx_membership'].search([]),
#         })

#     @http.route('/wx_membership/wx_membership/objects/<model("wx_membership.wx_membership"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wx_membership.object', {
#             'object': obj
#         })