# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import logging
from yuancloud import cache
from yuancloud.osv import fields, osv, expression
from yuancloud.tools.translate import _

logger = logging.getLogger(__name__)


def get_suite_token(suite_id, suite_secret, suite_ticket):
    key = suite_id + "suite_access_token"
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_suite_token"
    category_data = {
        "suite_id": suite_id,
        "suite_secret": suite_secret,
        "suite_ticket": suite_ticket
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" not in tokeninfo:
        token = tokeninfo["suite_access_token"]
        cache.redis.set(key, token, 600)
        return token
    else:
        raise osv.except_osv(_('Error!'), _('获取suite_access_token出错'))


def get_pre_auth_code(suite_id, suite_access_token):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_pre_auth_code?suite_access_token=" + suite_access_token
    category_data = {
        "suite_id": suite_id
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo["errcode"] == 0:
        return tokeninfo['pre_auth_code']
    else:
        raise osv.except_osv(_('Error!'), _('获取pre_auth_code出错'))


def set_session_info(suite_access_token, pre_auth_code, appid_list):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/set_session_info?suite_access_token=" + suite_access_token
    category_data = {
        "pre_auth_code": pre_auth_code,
        "session_info":
            {
                "appid": appid_list
            }
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo["errcode"] == 0:
        return True
    else:
        raise osv.except_osv(_('Error!'), _('设置授权配置出错'))


def get_permanent_code(suite_access_token, suite_id, auth_code):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?suite_access_token=" + suite_access_token
    category_data = {
        "suite_id": suite_id,
        "auth_code": auth_code
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if 'errcode' not in tokeninfo:
        return tokeninfo
    else:
        raise osv.except_osv(_('Error!'), _('获取永久授权码出错'))

# 获取企业号的授权信息
def get_auth_info(suite_access_token, suite_id, auth_corpid, permanent_code):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_auth_info?suite_access_token=" + suite_access_token
    category_data = {
        "suite_id": suite_id,
        "auth_corpid": auth_corpid,
        "permanent_code": permanent_code
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if 'errcode' not in tokeninfo:
        return tokeninfo
    else:
        raise osv.except_osv(_('Error!'), _('获取企业号授权信息出错'))

def get_corp_access_token(suite_access_token, suite_id, auth_corpid, permanent_code):
    key = suite_id + auth_corpid + "access_token"
    access_token = cache.redis.get(key)
    if access_token == None:
        category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_corp_token?suite_access_token=" + suite_access_token
        category_data = {
            "suite_id": suite_id,
            "auth_corpid": auth_corpid,
            "permanent_code": permanent_code
        }
        req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:' + html)
        tokeninfo = json.loads(html)
        print tokeninfo
        if 'errcode' not in tokeninfo:
            access_token = tokeninfo['access_token']
            cache.redis.set(key, access_token, 7100)
            return access_token
        else:
            raise osv.except_osv(_('Error!'), _('获取企业号授权信息出错'))
    else:
        return access_token

# 获取应用提供商凭证
def get_provider_token(providerid, provider_secret):
    key = providerid + "provider_access_token"
    access_token = cache.redis.get(key)
    if access_token == None:
        category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_provider_token"
        category_data = {
            "corpid": providerid,
            "provider_secret": provider_secret
        }
        req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:' + html)
        tokeninfo = json.loads(html)
        print tokeninfo
        if 'errcode' not in tokeninfo:
            access_token = tokeninfo['provider_access_token']
            cache.redis.set(key, access_token, 7100)
            return access_token
        else:
            raise osv.except_osv(_('Error!'), _('获取应用提供商凭证出错'))
    else:
        return access_token

# 获取企业号登录用户信息
def get_login_info(auth_code, access_token):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_login_info?access_token=" + access_token
    category_data = {
        "auth_code": auth_code
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if 'errcode' not in tokeninfo:
        return tokeninfo
    else:
        raise osv.except_osv(_('Error!'), _('获取企业号登录用户信息出错'))


# 获取登录企业号官网的url
def get_login_url(login_ticket, target, agentid, access_token):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/service/get_login_url?access_token=" + access_token
    if agentid == "":
        category_data = {
            "login_ticket": login_ticket,
            "target": target
        }
    else:
        category_data = {
            "login_ticket": login_ticket,
            "target": target,
            "agentid": agentid
        }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo['login_url']
    else:
        raise osv.except_osv(_('Error!'), _('获取登录企业号官网的url信息出错'))


def send_text_session(access_token, send_user, content, receiver_type, receiver_id):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/chat/send?access_token=" + access_token
    category_data = {
        "receiver":
            {
                "type": receiver_type,
                "id": receiver_id
            },
        "sender": send_user,
        "msgtype": "text",
        "text":
            {
                "content": content
            }
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return True
    else:
        raise osv.except_osv(_('Error!'), _('发送文本消息出错'))


def send_image_session(access_token, send_user, MediaID, receiver_type, receiver_id):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/chat/send?access_token=" + access_token
    category_data = {
        "receiver":
            {
                "type": receiver_type,
                "id": receiver_id
            },
        "sender": send_user,
        "msgtype": "image",
        "image":
            {
                "media_id": MediaID
            }
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return True
    else:
        raise osv.except_osv(_('Error!'), _('发送文本消息出错'))


def send_voice_session(access_token, send_user, MediaID, receiver_type, receiver_id):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/chat/send?access_token=" + access_token
    category_data = {
        "receiver":
            {
                "type": receiver_type,
                "id": receiver_id
            },
        "sender": send_user,
        "msgtype": "voice",
        "voice":
            {
                "media_id": MediaID
            }
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return True
    else:
        raise osv.except_osv(_('Error!'), _('发送文本消息出错'))


def send_file_session(access_token, send_user, MediaID, receiver_type, receiver_id):
    category_url = "https://qyapi.weixin.qq.com/cgi-bin/chat/send?access_token=" + access_token
    category_data = {
        "receiver":
            {
                "type": receiver_type,
                "id": receiver_id
            },
        "sender": send_user,
        "msgtype": "file",
        "file":
            {
                "media_id": MediaID
            }
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return True
    else:
        raise osv.except_osv(_('Error!'), _('发送文本消息出错'))
