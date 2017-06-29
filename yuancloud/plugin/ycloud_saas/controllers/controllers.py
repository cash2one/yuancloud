# -*- coding: utf-8 -*-
from yuancloud import http
from yuancloud.http import request
from yuancloud import tools
from yuancloud.tools.translate import _


class YcloudSaas(http.Controller):
    @http.route(['/my/database'], type='http', auth="public", website=True)
    def database(self):
        partner = request.env.user.partner_id

        clients = request.env['saas_portal.client'].sudo().search([('partner_id', '=', partner.id),('state','=','open')])
        urls = {}
        for client in clients:
            state = {
                'd': client.name,
                'client_id': client.client_id,
            }
            url = client.server_id._request(path='/saas_server/edit_database', state=state, client_id=client.client_id)
            urls[client.client_id] = url[0]
        values = {
            'urls': urls,
            'clients': clients,
            'company': request.website.company_id,
            'user': request.env.user
        }

        return request.website.render("ycloud_saas.database", values)
        # @http.route('/ycloud_saas/ycloud_saas/', auth='public')
        # def index(self, **kw):
        #     return "Hello, world"
        #
        # @http.route('/ycloud_saas/ycloud_saas/objects/', auth='public')
        # def list(self, **kw):
        #     return http.request.render('ycloud_saas.listing', {
        #         'root': '/ycloud_saas/ycloud_saas',
        #         'objects': http.request.env['ycloud_saas.ycloud_saas'].search([]),
        #     })
        #
        # @http.route('/ycloud_saas/ycloud_saas/objects/<model("ycloud_saas.ycloud_saas"):obj>/', auth='public')
        # def object(self, obj, **kw):
        #     return http.request.render('ycloud_saas.object', {
        #         'object': obj
        #     })
