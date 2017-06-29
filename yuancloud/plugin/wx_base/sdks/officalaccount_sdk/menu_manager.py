# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging

logger = logging.getLogger(__name__)


def create_menu_access_token(menuData, accessToken):
    logging.debug("accessToken:" + accessToken)
    createMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + accessToken
    req = urllib2.Request(createMenuUrl, (menuData).encode("utf-8"))
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    # import requests
    # res = requests.post(url=createMenuUrl, data=menuData, )
    create_menu_result = json.loads(html)
    if create_menu_result['errcode'] == 0:
        return "创建菜单成功"
    else:
        return "创建菜单失败:" + str(create_menu_result['errcode']) + create_menu_result['errmsg']


def query_menu_access_token(accessToken):
    queryMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=" + accessToken
    response = urllib2.urlopen(queryMenuUrl)
    html = response.read().decode("utf-8")
    # tokeninfo = json.loads(html,ensure_ascii=False)
    tokeninfo = json.loads(html)
    return tokeninfo


def delete_menu_access_token(accessToken):
    queryMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=" + accessToken
    response = urllib2.urlopen(queryMenuUrl)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return "删除菜单成功"
    else:
        return "删除菜单失败:" + tokeninfo['errmsg']


def create_addconditional_menu_access_token(menudata, accessToken):
    print accessToken
    logging.debug("accessToken:" + accessToken)
    createMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/addconditional?access_token=" + accessToken
    req = urllib2.Request(createMenuUrl, (menudata).encode("utf-8"))
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    print html
    create_menu_result = json.loads(html)
    return create_menu_result


def delete_addconditonal_menu_access_token(menuid, accessToken):
    queryMenuUrl = "https://api.weixin.qq.com/cgi-bin/menu/delconditional?access_token=" + accessToken
    menudata = {}
    menudata.update({
        "menuid": menuid
    })
    req = urllib2.Request(queryMenuUrl, json.dumps(menudata, ensure_ascii=False).encode('utf8'))
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    print html
    delete_menu_result = json.loads(html)
    return delete_menu_result


class menu_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    # 创建菜单
    def create_menu(self, menuData):
        menuData_new = ""
        if self._appid == "wx098ebed18e52ed29":
            # if self._appid=="wxc3d3865fb17a924b":
            menuData_new = '''{
            "button":[
            {
            "name":"微社交",
            "sub_button":[
                 {
                    "type":"click",
                    "name":"会员卡",
                    "key":"member_introduce"
                 },
                 {
                    "type":"click",
                    "name":"门店介绍",
                    "key":"store_introduce"
                 },
                 {
                    "type":"click",
                    "name":"资源合作",
                    "key":"resource"
                 },
                 {
                    "type":"click",
                    "name":"关于我们",
                    "key":"aboutus"
                 }
              ]
            },
            {
               "name":"享优惠",
               "sub_button":[
                  {
                     "type":"view",
                     "name":"幸运大抽奖",
                     "url":"http://wap.koudaitong.com/v2/apps/wheel?alias=rtd7dx4u"
                  },
                  {
                     "type":"view",
                     "name":"签到赢积分",
                     "url":"http://wap.koudaitong.com/v2/apps/checkin?alias=30hbtezs"
                  },
                  {
                     "type":"view",
                     "name":"疯狂猜猜猜",
                     "url":"http://wap.koudaitong.com/v2/apps/crazyguess?alias=bl4rahc4"
                  },
                  {
                     "type":"view",
                     "name":"生肖翻翻看",
                     "url":"http://wap.koudaitong.com/v2/apps/zodiac?alias=kl8w5fnw"
                  },
                  {
                     "type":"view",
                     "name":"优惠劵",
                     "url":"http://mp.weixin.qq.com/bizmall/cardshelf?shelf_id=1&showwxpaytitle=1&biz=MzAwNDY0MjQ3Mg==&t=cardticket/shelf_list&scene=1000007#wechat_redirect"
                  }
               ]
            },
            {
               "name":"微商城",
               "sub_button":[
                 {
                   "type":"click",
                    "name":"逛商城",
                    "key":"shopping"
                 },
                 {
                    "type":"click",
                    "name":"常见问题",
                    "key":"question"
                 },
                 {
                   "type":"click",
                    "name":"我的订单",
                    "key":"myorder"
                 }
               ]
            }
            ]
            }'''
        else:
            menuData_new = '''{
    "button": [
        {
            "name": "山水物源",
            "sub_button": [
                {
                    "type": "view",
                    "name": "关于我们",
                    "url": "http://mp.weixin.qq.com/s?__biz=MzAxODY0MDUxMg==&mid=207837847&idx=1&sn=4687faa3f9be4e7c9bb5bd054fc6d1a5#rd"
                },
                {
                    "type": "click",
                    "name": "资源合作",
                    "key": "contact"
                },
                {
                    "type": "click",
                    "name": "近期活动",
                    "key": "huodong"
                }
            ]
        },
        {
            "name": "购物乐园",
            "sub_button": [
                {
                    "type": "view",
                    "name": "掌柜推荐",
                    "url": "http://dwz.cn/11Ylup"
                },
                {
                    "type":"view",
                    "name":"微信小店",
                    "url":"http://mp.weixin.qq.com/bizmall/mallshelf?id=&t=mall/list&biz=MzAxODY0MDUxMg==&shelf_id=1&showwxpaytitle=1#wechat_redirect"
                },
                {
                    "type": "click",
                    "name": "我的订单",
                    "key": "myorder"
                },
                {
                    "type": "view",
                    "name": "免费上网",
                    "url": "http://wifi.weixin.qq.com/mbl/connect.xhtml?type=1"
                },
                {
                    "type": "click",
                    "name": "客服中心",
                    "key": "service"
                }
            ]
        },
        {
            "name": "养生资讯",
            "sub_button": [
                {
                    "type": "view",
                    "name": "杂文推荐",
                    "url": "http://mp.weixin.qq.com/s?__biz=MzAxODY0MDUxMg==&mid=207407836&idx=1&sn=985806546676df1e10ab41f9691beb59#rd"
                },
                {
                    "type": "view",
                    "name": "往期回顾",
                    "url": "http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzAxODY0MDUxMg==#wechat_webview_type=1&wechat_redirect"
                },
                {
                    "type": "view",
                    "name": "海参养生",
                    "url": "http://mp.weixin.qq.com/s?__biz=MzAxODY0MDUxMg==&mid=207447611&idx=4&sn=71528900b5b6622653f2a430e1d8dfd6#rd"
                },
                {
                    "type": "view",
                    "name": "养生攻略",
                    "url": "http://mp.weixin.qq.com/s?__biz=MzAxODY0MDUxMg==&mid=207407836&idx=1&sn=985806546676df1e10ab41f9691beb59#rd"
                }
            ]
        }
    ]
}'''
        if not menuData.strip():
            menuData = menuData_new
        print menuData
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        print accessToken
        return create_menu_access_token(menuData, accessToken)

    # 查询菜单
    def query_menu(self):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return query_menu_access_token(accessToken)

    # 删除菜单
    def delete_menu(self):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return delete_menu_access_token(accessToken)

    def create_addconditional_menu(self, menudata):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return create_addconditional_menu_access_token(menudata, accessToken)

    def delete_addconditional_menu(self, menuid):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return delete_addconditonal_menu_access_token(menuid, accessToken)
