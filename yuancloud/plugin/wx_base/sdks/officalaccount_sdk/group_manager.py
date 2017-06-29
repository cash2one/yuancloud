# -*- coding: utf-8 -*-
import urllib2
import json
import logging
import wx_public_sdk

logger = logging.getLogger(__name__)

def getall_group_access_token(access_token):
    logger.debug("query_order_access_token:" + access_token)
    interface_url = "https://api.weixin.qq.com/merchant/group/getall?access_token=" + access_token
    response = urllib2.urlopen(interface_url)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    return tokeninfo


def add_group_access_token(group_name, access_token):
    logger.debug("add_group_info_access_token:" + access_token)  # 默认增加库存
    interface_url = "https://api.weixin.qq.com/merchant/group/add?access_token=" + access_token
    post_data = {
        "group_detail": {
            "group_name": group_name,
        },
        "product_list": []
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    add_group_result = json.loads(html)
    print add_group_result
    return add_group_result


def modify_group_access_token(group_id, group_name, access_token):
    logger.debug("modify_group_info_access_token:" + access_token)  # 默认增加库存
    interface_url = "https://api.weixin.qq.com/merchant/group/propertymod?access_token=" + access_token
    post_data = {
        "group_id": group_id,
        "group_name": group_name
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    modify_group_result = json.loads(html)
    print modify_group_result
    return modify_group_result


def del_group_access_token(group_id, access_token):
    logger.debug("delete_group_info_access_token:" + access_token)  # 默认增加库存
    interface_url = "https://api.weixin.qq.com/merchant/group/del?access_token=" + access_token
    post_data = {
        "group_id": group_id
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    del_group_result = json.loads(html)
    print del_group_result
    return del_group_result


def getgroup_byid_access_token(group_id, access_token):
    logger.debug("getbyid_group_info_access_token:" + access_token)  # 默认增加库存
    interface_url = "https://api.weixin.qq.com/merchant/group/getbyid?access_token=" + access_token
    post_data = {
        "group_id": group_id
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    get_group_result = json.loads(html)
    print get_group_result
    return get_group_result


def product_mod_group_access_token(group_id, product_id, mod_action, access_token):
    logger.debug("product_mod_group_info_access_token:" + access_token)  # 默认增加库存
    interface_url = "https://api.weixin.qq.com/merchant/group/productmod?access_token=" + access_token
    post_data = {
        "group_id": group_id,
        "product": [{
            "product_id": product_id,
            "mod_action": mod_action
        }]
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    product_mod_group_result = json.loads(html)
    print product_mod_group_result
    return product_mod_group_result


class group_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    # 获取所有分组
    def getall_group(self):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return getall_group_access_token(access_token)

    # 增加分组
    def add_group(self, group_name):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return add_group_access_token(group_name, access_token)

    # 修改分组属性
    def modify_group(self, group_id, group_name):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return modify_group_access_token(group_id, group_name, access_token)

    # 删除分组
    def del_group(self, group_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return del_group_access_token(group_id, access_token)

    # 根据分组ID获取分组信息
    def getbyid_group(self, group_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return getgroup_byid_access_token(group_id, access_token)

    # 修改分组商品
    def product_mod_group(self, group_id, product_id, mod_action):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return product_mod_group_access_token(group_id, product_id, mod_action, access_token)
