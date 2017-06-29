# -*- coding: utf-8 -*-

import hashlib
import random
import string
import urllib2
import simplejson
from yuancloud import http
from yuancloud.http import request
import time
import wechatpy
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException

from yuancloud import cache

MODULE_BASE_PATH = '/wx/app/'


class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        str_sign = '&'.join(
            ['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(str_sign).hexdigest()
        return self.ret


class WxController(http.Controller):
    def get_token(self, appid=None, secret=None):
        if not all([appid, secret]):
            appid, secret = self._get_appid_sec()
        access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
            appid, secret)

        access_token = cache.redis.get(appid + '_access_token')
        if not access_token or access_token == 'None':
            token = urllib2.urlopen(access_token_url).read()
            access_token = simplejson.loads(token).get('access_token', None)

            cache.redis.set(appid + '_access_token', access_token, 7000)

        return access_token

    def _get_appid_sec(self):
        return 'wxadf2fd0df3523bed', '0c99675b9e4c90d893755c5f4815a0b9'
        weixin = request.env['ycloud.oauth.weixin'].sudo()
        providers = weixin.search(
            [('enabled', '=', True), ('login_type', '=', 'enterprise')])
        if not providers:
            return None, None
        appid = providers[0]["appid"]
        secret = providers[0]["secret"]

        return appid, secret

    def download_media(self, media_id):
        token = self.get_token()
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s' % (
            token, media_id)
        response = urllib2.urlopen(url).read()
        return response

    def get_wechat_config(self, url):
        appid, secret = self._get_appid_sec()
        if not all([appid, secret]):
            return
        access_token = self.get_token(appid, secret)
        return self.getsign(appid, secret, access_token, url)

    def getsign(self, appid, secret, access_token, url):
        ticket_url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi" % access_token
        ticket_token = cache.redis.get(appid + '_ticket_token')
        if not ticket_token:
            token = urllib2.urlopen(ticket_url).read()
            ticket_token = simplejson.loads(
                token).get('ticket').encode('utf-8')

            cache.redis.set(appid + '_ticket_token', ticket_token, 7000)
        s = Sign(ticket_token, url)
        ret = s.sign()
        ret["appid"] = appid
        return simplejson.dumps(ret)

    @http.route(MODULE_BASE_PATH + 'getwechatapidata', type='http', auth="none", csrf=False)
    def getwechatapidata(self, **kwargs):
        if 'url' in kwargs:
            configJson = self.get_wechat_config(kwargs['url'])
            return configJson

    @http.route(MODULE_BASE_PATH + 'weixin_callback', type='http', auth="user")
    def weixin_callback(self, **kwargs):
        crypto = WeChatCrypto(Token, EncodingAESKey, CorpId)
        msg_signature, timestamp, nonce = kwargs[
            'msg_signature'], kwargs['timestamp'], kwargs['nonce']
        if request.httprequest.method == 'GET':
            try:
                echostr = crypto.check_signature(
                    msg_signature,
                    timestamp,
                    nonce,
                    kwargs['echostr'],
                )
            except InvalidSignatureException:
                return 'error'
            return echostr
        else:
            try:
                msg = crypto.decrypt_message(
                    request.httprequest.data,
                    msg_signature,
                    timestamp,
                    nonce,
                )
                msg = wechatpy.parse_message(msg)

                if msg.event == 'subscribe':
                    url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=%s&userid=%s' % (
                        self.get_token(), msg.source)
                    userinfo = urllib2.urlopen(url).read()

                    ormenv = request.env
                    employee = ormenv['hr.employee'].sudo().search(
                        [('user_id', '=', msg.source)])
                    employee.corp_weixinid = simplejson.loads(
                        userinfo).get('weixinid')

                    reply = wechatpy.replies.ArticlesReply(message=msg)

                    reply.add_article({
                        'title': '欢迎关注',
                        'description': '欢迎您关注',
                        # 'image': 'image url',
                        'url': request.httprequest.host_url + 'mobile/ui/home',
                    })
                    return crypto.encrypt_message(reply.render(), nonce, timestamp)

                return 'ok'
                if msg.type == 'text':
                    reply = wechatpy.create_reply(msg.content, msg)
                else:
                    reply = wechatpy.create_reply(
                        'Sorry, can not handle this for now', msg)
                return crypto.encrypt_message(reply.render(), nonce, timestamp)

            except InvalidSignatureException:
                return 'error'


Token = "T6t3WENCqULbuu"
EncodingAESKey = "Di6e2EPQHBXhp4kSe9WB53JOIljqOADr247QVvl9Tl3"
CorpId = "wx676ea50e6f31a650"
