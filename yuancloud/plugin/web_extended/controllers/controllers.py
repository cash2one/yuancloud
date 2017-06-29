# -*- coding: utf-8 -*-
from yuancloud import http

# class WebExtended(http.Controller):
#     @http.route('/web_extended/web_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/web_extended/web_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('web_extended.listing', {
#             'root': '/web_extended/web_extended',
#             'objects': http.request.env['web_extended.web_extended'].search([]),
#         })

#     @http.route('/web_extended/web_extended/objects/<model("web_extended.web_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('web_extended.object', {
#             'object': obj
#         })