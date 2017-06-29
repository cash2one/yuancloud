# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging

logger = logging.getLogger(__name__)


def query_poilist_access_token(begin, limit, access_token):
    logger.debug("query_poilist_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/cgi-bin/poi/getpoilist?access_token=" + access_token
    postdata = {}
    postdata.update({
        "begin": begin,
        "limit": limit
    })
    req = urllib2.Request(category_url, json.dumps(postdata, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    return tokeninfo


class poi_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    def query_poilist(self, begin, limit):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return query_poilist_access_token(begin, limit, access_token)
