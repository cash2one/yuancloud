# -*- coding: utf-8 -*-
import time
import os
import urllib2,json,urllib
import public_sdk
import logging

logger = logging.getLogger(__name__)

class menu_manager:

    def __init__(self,AppId,AppSercret):
        self._appid=AppId
        self._appsercret=AppSercret

    #创建菜单
    def create_menu(self,menuData,agentid):
        print menuData
        wxsdk=public_sdk.public_sdk(self._appid,self._appsercret)
        accessToken=wxsdk.getAccessToken()
        print accessToken
        logging.debug("accessToken:"+accessToken)
        createMenuUrl = "https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token="+accessToken+"&agentid="+agentid
        req=urllib2.Request(createMenuUrl,(menuData).encode("utf-8"))
        response=urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        #import requests
        #res = requests.post(url=createMenuUrl, data=menuData, )
        create_menu_result = json.loads(html)
        if create_menu_result['errcode']==0:
            return "创建菜单成功"
        else :
            return "创建菜单失败:"+str(create_menu_result['errcode'])+create_menu_result['errmsg']

    #查询菜单
    def query_menu(self,agentid):
        wxsdk=public_sdk.public_sdk(self._appid,self._appsercret)
        accessToken=wxsdk.getAccessToken()
        queryMenuUrl="https://qyapi.weixin.qq.com/cgi-bin/menu/get?access_token="+accessToken+"&agentid="+agentid
        response = urllib2.urlopen(queryMenuUrl)
        html = response.read().decode("utf-8")
        #tokeninfo = json.loads(html,ensure_ascii=False)
        tokeninfo = json.loads(html)
        return tokeninfo

    #删除菜单
    def delete_menu(self,agentid):
        wxsdk=public_sdk.public_sdk(self._appid,self._appsercret)
        accessToken=wxsdk.getAccessToken()
        queryMenuUrl="https://qyapi.weixin.qq.com/cgi-bin/menu/delete?access_token="+accessToken+"&agentid="+agentid
        response = urllib2.urlopen(queryMenuUrl)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        if tokeninfo['errcode']==0:
            return "删除菜单成功"
        else :
            return "删除菜单失败:"+tokeninfo['errmsg']