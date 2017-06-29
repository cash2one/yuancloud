# -*- coding: utf-8 -*-
import time
import os
import urllib2,json,urllib
import logging
from yuancloud import cache

_logger = logging.getLogger(__name__)

class public_sdk:
    

    def __init__(self,AppId,AppSercret):
        self._appid=AppId
        self._appSercret=AppSercret

    #获取AccessToken    
    def getAccessToken(self):
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (self._appid, self._appSercret)
        #return url;
        key=self._appid+self._appSercret + '_access_token'
        #mc = getClient()
        token =cache.redis.get(key)
        if token == None:            
            response = urllib2.urlopen(access_token_url)
            html = response.read().decode("utf-8")
            tokeninfo = json.loads(html)
            if "errcode" in tokeninfo:
                return u"获取AccessToken出错"+str(tokeninfo['errcode'])+tokeninfo['errmsg']                    
            else:                          
                token = tokeninfo['access_token']
                logging.debug("token:"+token)
                cache.redis.set(key, token,7200)
                #mc.set(key, token, 7200)
                return token
        token =cache.redis.get(key)
        logging.debug("getAccessToken:"+token)
        return token

    def get_jsapi_ticket(self):
        access_token=self.getAccessToken()
        print access_token
        url="https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token="+access_token
        key=self._appid + '_ticket_token'
        js_sdk_token=cache.redis.get(key)
        if js_sdk_token==None:
            response = urllib2.urlopen(url)
            html = response.read().decode("utf-8")
            tokeninfo = json.loads(html)
            if tokeninfo['errcode']==0:
                token = tokeninfo['ticket']
                logging.debug("js_token:"+token)
                cache.redis.set(key, token,7200)
            else:
                return u"获取JS Ticket出错:"+str(tokeninfo['errcode'])+","+tokeninfo['errmsg']
        js_sdk_token=cache.redis.get(key)
        return  js_sdk_token
