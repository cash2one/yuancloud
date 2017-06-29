# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging

_logger = logging.getLogger(__name__)


def send_template_access_token(postdata, access_token):
    _logger.debug("send_templdate_access_token:" + access_token)
    setformurl = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(setformurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


class template_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    def send_templdate(self, postdata):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return send_template_access_token(postdata, access_token)

    def sendtemplateMessage(self, template_id, frist_value, remark_value, transaction_id, openid, total_fee, qulatiy,
                            time_end, bank_type, companyname):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        _logger.debug("sendtemplateMessage_access_token:" + access_token)
        postdata = {
            "touser": openid,
            "template_id": template_id,
            "url": "",
            "data": {
                "first": {
                    "value": frist_value,
                    "color": "#173177"
                },
                "keyword1": {
                    "value": total_fee,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": qulatiy,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": time_end,
                    "color": "#173177"
                },
                "keyword4": {
                    "value": transaction_id,
                    "color": "#173177"
                },
                "keyword5": {
                    "value": companyname,
                    "color": "#173177"
                },
                "remark": {
                    "value": remark_value,
                    "color": "#173177"
                }
            }
        }
        setformurl = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + access_token
        data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
        print data
        req = urllib2.Request(setformurl, data)
        req.add_header("Content-Type", "application/json")
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        print tokeninfo
        if tokeninfo['errcode'] == 0:
            return "发送支付模板信息成功"
        else:
            return "发送支付模板信息失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
