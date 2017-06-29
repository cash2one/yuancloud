# -*- coding: utf-8 -*-
from yuancloud import http

# class WebsitesaleAddressHidden(http.Controller):
#     @http.route('/websitesale_address_hidden/websitesale_address_hidden/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/websitesale_address_hidden/websitesale_address_hidden/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('websitesale_address_hidden.listing', {
#             'root': '/websitesale_address_hidden/websitesale_address_hidden',
#             'objects': http.request.env['websitesale_address_hidden.websitesale_address_hidden'].search([]),
#         })

#     @http.route('/websitesale_address_hidden/websitesale_address_hidden/objects/<model("websitesale_address_hidden.websitesale_address_hidden"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('websitesale_address_hidden.object', {
#             'object': obj
#         })