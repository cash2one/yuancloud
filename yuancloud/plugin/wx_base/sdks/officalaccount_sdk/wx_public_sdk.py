# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import logging
from yuancloud import cache

# 获取MemCache客户端
def getClient():
    mc = ""
    return mc

_logger = logging.getLogger(__name__)


def create_qrcode_access_token(expire_seconds, scene_id, access_token):
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + access_token
    create_qrcode_data = {
        "expire_seconds": expire_seconds,
        "action_name": "QR_SCENE",
        "action_info": {
            "scene": {
                "scene_id": scene_id
            }
        }
    }
    req = urllib2.Request(url, json.dumps(create_qrcode_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if 'errcode' in tokeninfo:
        return "生成临时二维码出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


def create_qr_limit_code_int_access_token(scene_id, access_token):
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + access_token
    create_qr_limit_data = {
        "action_name": "QR_LIMIT_SCENE",
        "action_info": {
            "scene": {
                "scene_id": scene_id
            }
        }
    }
    req = urllib2.Request(url, json.dumps(create_qr_limit_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if 'errcode' in tokeninfo:
        return "生成永久二维码出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


def create_qr_limit_code_str_access_token(scene_str, access_token):
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + access_token
    create_qr_limit_str_data = {
        "action_name": "QR_LIMIT_STR_SCENE",
        "action_info": {
            "scene": {
                "scene_str": scene_str
            }
        }
    }
    req = urllib2.Request(url, json.dumps(create_qr_limit_str_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if 'errcode' in tokeninfo:
        return "生成永久二维码出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


def create_long2short_access_token(access_token, longurl):
    url = "https://api.weixin.qq.com/cgi-bin/shorturl?access_token=" + access_token
    create_qr_limit_str_data = {
        "action": "long2short",
        "long_url": {
            longurl
        }
    }
    req = urllib2.Request(url, json.dumps(create_qr_limit_str_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return u"长链接转短链接出错:" + str(tokeninfo['errcode']) + "," + tokeninfo['errmsg']


def get_card_js_ticket_access_token(access_token, appid):
    url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=" + access_token + "&type=wx_card"
    key = "card_js_ticket" + appid
    # mc = getClient()
    token = cache.redis.get(key)
    if token == None:
        response = urllib2.urlopen(url)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        if "ticket" in tokeninfo:
            token = tokeninfo['ticket']
            logging.debug("card_js_ticket:" + token)
            cache.redis.set(key, token, 7200)
            # return token
        else:
            return u"获取card_js_ticket出错" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    token = cache.redis.get(key)
    logging.debug("card_js_ticket:" + token)
    return token


def get_jsapi_ticket_access_token(access_token, appid):
    print access_token
    url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=" + access_token + "&type=jsapi"
    key = "jsapi" + appid
    print url
    print key
    js_sdk_token = cache.redis.get(key)
    if js_sdk_token == None:
        response = urllib2.urlopen(url)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        if tokeninfo['errcode'] == 0:
            token = tokeninfo['ticket']
            logging.debug("js_token:" + token)
            cache.redis.set(key, token, 7200)
        else:
            return u"获取JS Ticket出错:" + str(tokeninfo['errcode']) + "," + tokeninfo['errmsg']
    js_sdk_token = cache.redis.get(key)
    return js_sdk_token


class wx_public_sdk:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    # 获取AccessToken
    def getAccessToken(self):
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + self._appid + "&secret=" + self._appSercret
        # return url;
        key = "publicToken" + self._appid
        # mc = getClient()
        token = cache.redis.get(key)
        if token == None:
            response = urllib2.urlopen(url)
            html = response.read().decode("utf-8")
            tokeninfo = json.loads(html)
            if "errcode" in tokeninfo:
                return u"获取AccessToken出错" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
            else:
                token = tokeninfo['access_token']
                logging.debug("token:" + token)
                cache.redis.set(key, token, 7200)
                # mc.set(key, token, 7200)
                return token
        token = cache.redis.get(key)
        logging.debug("getAccessToken:" + token)
        return token

    # 生成临时二维码
    def create_qrcode(self, expire_seconds, scene_id):
        access_token = self.getAccessToken()
        return create_qrcode_access_token(expire_seconds, scene_id, access_token)

    # 生成永久二维码 整型
    def create_qr_limit_code_int(self, scene_id):
        access_token = self.getAccessToken()
        return create_qr_limit_code_int_access_token(scene_id, access_token)

    # 生成永久二维码 字符型
    def create_qr_limit_code_str(self, scene_str):
        access_token = self.getAccessToken()
        return create_qr_limit_code_str_access_token(scene_str, access_token)

    # 获取二维码图片信息
    def get_qrcode_image(self, ticket):
        url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + ticket
        response = urllib2.urlopen(url)
        html = response.read().decode("utf-8")
        return html

    def create_long2short(self, longurl):
        access_token = self.getAccessToken()
        return create_long2short_access_token(access_token, longurl)

    def get_card_js_ticket(self):
        access_token = self.getAccessToken()
        return get_card_js_ticket_access_token(access_token, self._appid)

    def get_jsapi_ticket(self):
        access_token = self.getAccessToken()
        return get_jsapi_ticket_access_token(access_token, self._appid)
