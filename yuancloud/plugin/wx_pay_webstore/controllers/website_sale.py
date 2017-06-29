__author__ = 'sswy'
# -*- coding: utf-8 -*-
import yuancloud
from yuancloud import http
from yuancloud.http import request
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import user_manager
import werkzeug.urls
import werkzeug.exceptions
from yuancloud import SUPERUSER_ID
from yuancloud.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class website_sale(yuancloud.addons.website_sale.controllers.main.website_sale):
    @http.route()
    def shop(self, page=0, category=None, search='', **post):
        code=""
        payment_mode=request.env['payment.acquirer'].search([('provider', '=', 'weixin')])[0]
        appid= payment_mode.weixin_officialaccount.wx_appid
        _logger.info("appid:"+appid)
        appsecret=payment_mode.weixin_officialaccount.wx_appsecret
        _logger.info("appsecret:"+appsecret)
        usermanager=user_manager.user_manager(appid,appsecret)
        if 'MicroMessenger' in request.httprequest.user_agent.string:
            try:
                code=request.params["code"]
            except:
                code=""
            print code
            if code=="":
                redirect_url=request.httprequest.url
                #redirect_url=redirect_url.replace('www.','')
                scope="snsapi_base"
                menuresult=usermanager.create_auth_url(redirect_url,scope)
                print menuresult
                return werkzeug.utils.redirect(menuresult)
            userinfo=usermanager.get_useropenid_code(code)
            openid="123123"
            try:
                try:
                    import simplejson as json
                except ImportError:
                    import json
                print json.dumps(userinfo)
                openid=userinfo['openid']
            except:
                print 3
                openid="1323222"
            print 5
            print openid
            _logger.info("openid:"+openid)
            http.request.session['openid'] = openid
        return super(website_sale, self).shop(page, category, search, **post)


