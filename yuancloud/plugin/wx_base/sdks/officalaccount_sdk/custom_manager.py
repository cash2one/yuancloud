# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)


def sendnews_custommessage_access_token(openid, newslist, kf_account, access_token):
    _logger.debug("sendText_custommessage_access_token:" + access_token)
    postdata = {}
    if kf_account == "":
        postdata = {
            "touser": openid,
            "msgtype": "news",
            "news":
                {
                    "articles": newslist
                }
        }
    else:
        postdata = {
            "touser": openid,
            "msgtype": "news",
            "news":
                {
                    "articles": newslist
                },
            "customservice":
                {
                    "kf_account": kf_account
                }
        }
    del_card_url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(del_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


def sendImage_custommessage_access_token(openid, mediaid, kf_account, access_token):
    _logger.debug("sendText_custommessage_access_token:" + access_token)
    postdata = {}
    if kf_account == "":
        postdata = {
            "touser": openid,
            "msgtype": "image",
            "image":
                {
                    "media_id": mediaid
                }
        }
    else:
        postdata = {
            "touser": openid,
            "msgtype": "image",
            "image":
                {
                    "media_id": mediaid
                },
            "customservice":
                {
                    "kf_account": kf_account
                }
        }
    del_card_url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(del_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo

def sendText_custommessage_access_token(openid, content, kf_account, access_token):
    _logger.debug("sendText_custommessage_access_token:" + access_token)
    postdata = {}
    if kf_account == "":
        postdata = {
            "touser": openid,
            "msgtype": "text",
            "text":
                {
                    "content": content
                }
        }
    else:
        postdata = {
            "touser": openid,
            "msgtype": "text",
            "text":
                {
                    "content": content
                },
            "customservice":
                {
                    "kf_account": kf_account
                }
        }
    del_card_url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(del_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo

def sendMusic_custommessage_access_token(openid,title,description,musicurl,hqmusicurl,thumb_media_id,kf_account,access_token):
    _logger.debug("sendMusic_custommessage_access_token:" + access_token)
    postdata = {}
    if kf_account == "":
        postdata = {
            "touser": openid,
            "msgtype": "music",
            "music":
                {
                    "title":title,
      "description":description,
      "musicurl":musicurl,
      "hqmusicurl":hqmusicurl,
      "thumb_media_id":thumb_media_id
                }
        }
    else:
        postdata = {
            "touser": openid,
            "msgtype": "music",
            "music":
                {
                    "title":title,
      "description":description,
      "musicurl":musicurl,
      "hqmusicurl":hqmusicurl,
      "thumb_media_id":thumb_media_id
                },
            "customservice":
                {
                    "kf_account": kf_account
                }
        }
    del_card_url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(del_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


class custom_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    def sendnews_custommessage(self, openid, newslist, kf_account):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return sendnews_custommessage_access_token(openid, newslist, kf_account, access_token)

    def sendImage_custommessage(self, openid, mediaid, kf_account):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return sendImage_custommessage_access_token(openid, mediaid, kf_account, access_token)

    def sendText_custommessage(self, openid, content, kf_account):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return sendText_custommessage_access_token(openid, content, kf_account, access_token)


    def sendMusic_custommesage(self,openid,title,description,musicurl,hqmusicurl,thumb_media_id,kf_account):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return sendMusic_custommessage_access_token(openid, title,description,musicurl,hqmusicurl,thumb_media_id, kf_account, access_token)

