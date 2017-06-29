# -*- coding: utf-8 -*-
from yuancloud import http

# class ProfessionalTemplates(http.Controller):
#     @http.route('/professional_templates/professional_templates/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/professional_templates/professional_templates/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('professional_templates.listing', {
#             'root': '/professional_templates/professional_templates',
#             'objects': http.request.env['professional_templates.professional_templates'].search([]),
#         })

#     @http.route('/professional_templates/professional_templates/objects/<model("professional_templates.professional_templates"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('professional_templates.object', {
#             'object': obj
#         })