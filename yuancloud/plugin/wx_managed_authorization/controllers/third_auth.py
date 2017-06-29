# -*- coding: utf-8 -*-
from yuancloud import  http
import threading
import sys
from yuancloud import cache
reload(sys)
sys.setdefaultencoding('utf-8')
from openerp.api import Environment
import os
import sys
import jinja2
import random
import time

try:
    import simplejson as json
except ImportError:
    import json

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('yuancloud.addons.wx_managed_authorization', "views")

env_jinjia = jinja2.Environment(loader=loader, autoescape=True)
env_jinjia.filters["json"] = json.dumps


class third_auth(http.Controller):

    @http.route('/ycloud_base/user_auth_info',auth='none',csrf=False)
    def auth_info(self,**kw):
        print kw
        open_platurl=cache.redis.get('url') #服务开放平台
        third_platurl=cache.redis.get('baseurl'+"tjb8b3ddf76ca38321")#第三方应用
        session_platurl=cache.redis.get('baseurl'+'tjeaae807dcefd96c8') #会话服务
        customer_platurl=cache.redis.get('baseurl'+'tj0072de65cebdab77')#客服服务
        enterprise_loginurl=cache.redis.get('authurl')
        return env_jinjia.get_template("third_auth.html").render({
            "open_platurl": open_platurl,
            "third_platurl": third_platurl,
            "session_platurl": session_platurl,
            "customer_platurl": customer_platurl,
            "enterprise_loginurl": enterprise_loginurl
        })

    @http.route('/ycloud_base/register/', auth='none', methods=['post', 'get'],csrf=False)
    def register(self, **kw):
        print kw
        return env_jinjia.get_template("register.html").render({

        })

    @http.route('/ycloud_base/crm', auth='none', methods=['post', 'get'],csrf=False)
    def code(self, **kw):
        deliverycode = random.randint(1000, 9999)
        return str(deliverycode)
        # path = os.path.realpath(os.path.join(os.path.dirname(__file__)))
        # captcha_image = captcha(drawings=[
        #     background(),
        #     text(fonts=[
        #         os.path.join(path, 'fonts/arial.ttf'),
        #     ],
        #         drawings=[
        #             warp(),
        #             rotate(),
        #             offset()
        #         ]),
        #     curve(),
        #     noise(),
        #     smooth()
        # ])
        # code = random.sample(string.uppercase + string.digits, 4)
        # print code
        # request.session['captcha'] = ''.join(code)
        # image = captcha_image(code)
        # buf = StringIO()
        # image.save(buf, 'PNG', quality=70)
        # return base64.b64encode(buf.getvalue())

    @http.route('/ycloud_base/register/checkIfExist', auth='none', methods=['post', 'get'],csrf=False)
    def checkIfExist(self, **kw):
        print kw
        # data={}
        # data.update({
        #     ""
        # })
        # return simplejson.dumps()
        return "-1"

    @http.route('/ycloud_base/register/register', auth='none', methods=['post', 'get'],csrf=False)
    def regiser(self, **kw):
        print kw
        data = {}
        data.update({
            'success': True,
            'msg': ''
        })
        return json.dumps(data)

    @http.route('/ycloud_base/login_success', auth='none', methods=['post', 'get'],csrf=False)
    def login_success(self, **kw):
        print kw
        auth_code = kw['auth_code']
        # corpid = "wxe28ca91a338a7638"
        # provider_secret = "zV_Uc1zkcmJ7Uon1V7qZOhROPMPTIoO0LmqmrAYXbQRKhz1XjrBBswZhn3vidiZh"
        # provider_access_token = qy_open_public_sdk.get_provider_token(corpid, provider_secret)
        # print provider_access_token
        # auth_info = qy_open_public_sdk.get_login_info(auth_code, provider_access_token)
        # print auth_info
        return 'success'

    @http.route('/ycloud_base/login', auth='none', methods=['post', 'get'],csrf=False)
    def login(self, **kw):
        print kw
        timestamp = int(time.time())
        redirect_login_url = http.request.httprequest.host_url + "ycloud_base/login_success/"
        authurl = "https://qy.weixin.qq.com/cgi-bin/loginpage?corp_id=wxe28ca91a338a7638&redirect_uri=" + redirect_login_url + "&state=" + str(
            timestamp) + "&usertype=admin"
        return env_jinjia.get_template("login.html").render({
            "authurl": authurl
        })


