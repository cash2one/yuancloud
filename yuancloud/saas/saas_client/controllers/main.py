# -*- coding: utf-8 -*-
import werkzeug
import yuancloud
from yuancloud import http, SUPERUSER_ID
from yuancloud.http import request
import simplejson
from yuancloud.addons.auth_oauth.controllers.main import OAuthLogin as Home
from yuancloud.addons.web.controllers.main import ensure_db
import logging

_logger = logging.getLogger(__name__)


class SaasClient(http.Controller):
    @http.route(['/saas_client/new_database',
                 '/saas_client/edit_database'], type='http', auth='none')
    def new_database(self, **post):
        params = post.copy()
        state = simplejson.loads(post.get('state'))
        if not state.get('p'):
            state['p'] = request.env.ref('saas_server.saas_oauth_provider').id
        params['state'] = simplejson.dumps(state)
        return werkzeug.utils.redirect('/auth_oauth/signin?%s' % werkzeug.url_encode(params))


class SaaSClientLogin(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        param_model = request.env['ir.config_parameter']
        suspended = param_model.sudo().get_param('saas_client.suspended', '0')
        page_for_suspended = param_model.sudo().get_param('saas_client.page_for_suspended', '/')
        if suspended == '1':
            return werkzeug.utils.redirect(page_for_suspended, 303)
        return super(SaaSClientLogin, self).web_login(redirect, **kw)
