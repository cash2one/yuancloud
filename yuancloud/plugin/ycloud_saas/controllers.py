# -*- coding: utf-8 -*-
from yuancloud import http

# class YcloudSaas(http.Controller):
#     @http.route('/ycloud_saas/ycloud_saas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ycloud_saas/ycloud_saas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ycloud_saas.listing', {
#             'root': '/ycloud_saas/ycloud_saas',
#             'objects': http.request.env['ycloud_saas.ycloud_saas'].search([]),
#         })

#     @http.route('/ycloud_saas/ycloud_saas/objects/<model("ycloud_saas.ycloud_saas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ycloud_saas.object', {
#             'object': obj
#         })