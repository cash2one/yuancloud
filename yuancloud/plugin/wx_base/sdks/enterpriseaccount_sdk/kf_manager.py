# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import public_sdk
import logging

logger = logging.getLogger(__name__)


class kf_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    def sendtextmessage(self, sender_type, sender_value, recevice_type, recevice_value, content):
        wx_public = public_sdk.public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        postdata = {
            "sender":
                {
                    "type":sender_type,
                    "id": sender_value
                },
            "receiver":
                {
                    "type": recevice_type,
                    "id": recevice_value
                },
            "msgtype": "text",
            "text":
                {
                    "content": content
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
