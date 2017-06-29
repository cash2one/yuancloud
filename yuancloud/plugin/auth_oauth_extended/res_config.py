# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

from yuancloud.osv import osv, fields

import logging

_logger = logging.getLogger(__name__)


class base_config_settings(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'auth_oauth_weixin_openplatform_enabled': fields.boolean('允许用户通过微信开发平台账户PC端扫码登录'),
        #'auth_oauth_weixin_openplatform_appid': fields.char('AppID'),
        #'auth_oauth_weixin_openplatform_appsercret': fields.char('Appsercret'),
        'auth_oauth_openplatform':fields.many2one('wx.webapplication',string="开放平台网页应用"),
        'auth_oauth_weixin_officialaccount_enabled': fields.boolean('允许用户通过微信服务号登录'),
        'auth_oauth_officialaccount':fields.many2one('wx.officialaccount',string="服务号应用"),
        'auth_oauth_weixin_qyh_enabled': fields.boolean('允许用户通过微信企业号登录'),
        'auth_oauth_qyh':fields.many2one('wx.officialaccount',string="企业号应用"),
    }

    _defaults = {
        "auth_signup_uninvited": "True",
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(base_config_settings, self).default_get(cr, uid, fields, context=context)
        res.update(self.get_oauth_openplatfrom_providers(cr, uid, fields, context=context))
        res.update(self.get_oauth_wx_providers(cr,uid,fields,context=context))
        res.update(self.get_oauth_qyh_providers(cr,uid,fields,context=context))
        return res

    def get_oauth_openplatfrom_providers(self, cr, uid, fields, context=None):
        google_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_pcweixin')[1]
        rg = self.pool.get('auth.oauth.provider').read(cr, uid, [google_id], ['enabled', 'client_id', 'client_sercret'],
                                                       context=context)
        platform_id = self.pool.get('wx.webapplication').search(cr, uid,
                                                                   [('wx_webappid','=',rg[0]['client_id']),('wx_webappsecret','=',rg[0]['client_sercret'])],
                                                                   context=context)
        #platform_id=self.pool.get('wx.third_platform').search(cr,uid,[('auth_component_appid','=',rg[0]['client_id']),('auth_component_appsecret','=',rg[0]['client_sercret'])],context)
        if platform_id:
            return {
                'auth_oauth_weixin_openplatform_enabled': rg[0]['enabled'],
                'auth_oauth_openplatform': platform_id[0],
            #'auth_oauth_weixin_openplatform_appsercret': rg[0]['client_sercret'],
            }
        else:
            return {
                'auth_oauth_weixin_openplatform_enabled': rg[0]['enabled'],
                'auth_oauth_openplatform':False,
            }

    def get_oauth_wx_providers(self, cr, uid, fields, context=None):
        google_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_wx')[1]
        rg = self.pool.get('auth.oauth.provider').read(cr, uid, [google_id], ['enabled', 'client_id', 'client_sercret'],
                                                       context=context)
        platform_id = self.pool.get('wx.officialaccount').search(cr, uid,
                                                                   [('wx_appid','=',rg[0]['client_id']),('wx_appsecret','=',rg[0]['client_sercret']),('is_qyhapp','=',False)],
                                                                   context=context)
        #platform_id=self.pool.get('wx.third_platform').search(cr,uid,[('auth_component_appid','=',rg[0]['client_id']),('auth_component_appsecret','=',rg[0]['client_sercret'])],context)
        if platform_id:
            return {
                'auth_oauth_weixin_officialaccount_enabled': rg[0]['enabled'],
                'auth_oauth_officialaccount': platform_id[0],
            }
        else:
            return {
                'auth_oauth_weixin_officialaccount_enabled': rg[0]['enabled'],
                'auth_oauth_officialaccount':False,
            }

    def get_oauth_qyh_providers(self, cr, uid, fields, context=None):
        google_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_qyh')[1]
        rg = self.pool.get('auth.oauth.provider').read(cr, uid, [google_id], ['enabled', 'client_id', 'client_sercret'],
                                                       context=context)
        platform_id = self.pool.get('wx.officialaccount').search(cr, uid,
                                                                   [('wx_appid','=',rg[0]['client_id']),('wx_appsecret','=',rg[0]['client_sercret']),('is_qyhapp','=',True)],
                                                                   context=context)
        #platform_id=self.pool.get('wx.third_platform').search(cr,uid,[('auth_component_appid','=',rg[0]['client_id']),('auth_component_appsecret','=',rg[0]['client_sercret'])],context)
        if platform_id:
            return {
                'auth_oauth_weixin_qyh_enabled': rg[0]['enabled'],
                'auth_oauth_qyh': platform_id[0],
            }
        else:
            return {
                'auth_oauth_weixin_qyh_enabled': rg[0]['enabled'],
                'auth_oauth_qyh':False,
            }

    def set_oauth_providers(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        google_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_pcweixin')[1]
        rg = {
            'enabled': config.auth_oauth_weixin_openplatform_enabled,
            'client_id': config.auth_oauth_openplatform.wx_webappid,
            'client_sercret': config.auth_oauth_openplatform.wx_webappsecret,
            'provider_browser':'pc',
        }
        if config.auth_oauth_openplatform.wx_webappid:
            self.pool.get('auth.oauth.provider').write(cr, uid, [google_id], rg)
        auth_qyh_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_qyh')[1]
        rg = {
            'enabled': config.auth_oauth_weixin_qyh_enabled,
            'client_id': config.auth_oauth_qyh.wx_appid,
            'client_sercret': config.auth_oauth_qyh.wx_appsecret,
            'provider_browser':'weixin',
        }
        if config.auth_oauth_qyh.wx_appid:
            self.pool.get('auth.oauth.provider').write(cr, uid, [auth_qyh_id], rg)
        auth_wx_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'auth_oauth_extended', 'provider_wx')[1]
        rg = {
            'enabled': config.auth_oauth_weixin_officialaccount_enabled,
            'client_id': config.auth_oauth_officialaccount.wx_appid,
            'client_sercret': config.auth_oauth_officialaccount.wx_appsecret,
            'provider_browser':'weixin',
        }
        if config.auth_oauth_officialaccount.wx_appid:
            self.pool.get('auth.oauth.provider').write(cr, uid, [auth_wx_id], rg)
