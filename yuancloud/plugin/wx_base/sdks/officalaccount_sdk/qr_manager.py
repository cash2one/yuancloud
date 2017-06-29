# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging

logger = logging.getLogger(__name__)


def gen_gr_code_access_token(action_name, expire_seconds, scene_id, scene_str, access_token):
    logger.debug("gen_qr_code_access_token:" + access_token)
    gen_qr_url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + access_token
    postdata = ""
    if action_name == "QR_SCENE":
        postdata = {
            "expire_seconds": expire_seconds,
            "action_name": "QR_SCENE",
            "action_info":
                {
                    "scene":
                        {
                            "scene_id": scene_id
                        }
                }
        }
    elif action_name == "QR_LIMIT_SCENE":
        postdata = {
            "action_name": "QR_LIMIT_SCENE",
            "action_info":
                {"scene":
                    {
                        "scene_id": scene_id
                    }
                }
        }
    elif action_name == "QR_LIMIT_STR_SCENE":
        postdata = {
            "action_name": "QR_LIMIT_STR_SCENE",
            "action_info":
                {
                    "scene":
                        {
                            "scene_str": scene_str
                        }
                }
        }
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(gen_qr_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    gen_qr_result = json.loads(html)
    print gen_qr_result
    return gen_qr_result


class qr_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    def gen_qr_code(self, action_name, expire_seconds, scene_id, scene_str):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return gen_gr_code_access_token(action_name, expire_seconds, scene_id, scene_str, access_token)
