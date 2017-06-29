# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import logging
import public_sdk
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)


def send_customer_text_message_access_token(access_token, sender_type, sender_id, receiver_type, receiver_id,
                                            text_content):
    postdata = {
        "sender":
            {
                "type": sender_type,
                "id": sender_id
            },
        "receiver":
            {
                "type": receiver_type,
                "id": receiver_id
            },
        "msgtype": "text",
        "text":
            {
                "content": text_content
            }
    }
    sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/kf/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(sendmessageurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo

def sendtextmessage_access_token(agentid, content, userlist, partylist, taglist, issafe, access_token):
    postdata = {
        "touser": userlist,
        "toparty": partylist,
        "totag": taglist,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": content
        },
        "safe": issafe
    }
    sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(sendmessageurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo


class message_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    def sendtextmessage(self, agentid, content, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        sendtextmessage_access_token(agentid, content, userlist, partylist, taglist, issafe, access_token)

    def sendimagemessage(self, agentid, imageid, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "image",
            "agentid": agentid,
            "image": {
                "media_id": imageid
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo

    def sendvoicemessage(self, agentid, voiceid, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "voice",
            "agentid": agentid,
            "voice": {
                "media_id": voiceid
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo

    def sendfilemessage(self, agentid, fileid, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "file",
            "agentid": agentid,
            "file": {
                "media_id": fileid
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo

    def sendnewsmessage(self, agentid, newlist, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "news",
            "agentid": agentid,
            "news": {
                "articles": newlist
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo

    def sendmpnewsmessage(self, agentid, media_id, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "mpnews",
            "agentid": agentid,
            "mpnews": {
                "media_id": media_id
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo

    def sendmpnewsmessage_articles(self, agentid, articleslist, userlist, partylist, taglist, issafe):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "touser": userlist,
            "toparty": partylist,
            "totag": taglist,
            "msgtype": "mpnews",
            "agentid": agentid,
            "mpnews": {
                "articles": articleslist
            },
            "safe": issafe
        }
        sendmessageurl = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(sendmessageurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo
