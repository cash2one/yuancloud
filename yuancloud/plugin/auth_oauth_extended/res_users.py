# -*- coding: utf-8 -*-
import logging

import werkzeug.urls
import urlparse
import urllib2
import json

import yuancloud
from yuancloud.addons.auth_signup.res_users import SignupError
from yuancloud.osv import osv, fields
from yuancloud import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class res_users(osv.Model):
    _inherit = 'res.users'
    _columns = {
        'oauth_provider_extend':fields.one2many('oauth_provider_entity_extend','res_user_id', string="集成登录方式")
    }

class oauth_provider_entity_extend(osv.Model):
    _name = 'oauth_provider_entity_extend'
    _columns = {
        'res_user_id':fields.many2one('res.users','user_id'),
        'oauth_provider_id': fields.many2one('auth.oauth.provider', 'OAuth Provider'),
        'oauth_uid': fields.char('OAuth User ID', help="Oauth Provider user_id", copy=False),
        'oauth_access_token': fields.char('OAuth Access Token', readonly=True, copy=False),
    }
