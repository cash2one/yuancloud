# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging
from urllib import urlencode

logger = logging.getLogger(__name__)


def get_user_detailinfo_access_token(openid, access_token):
    user_url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=" + access_token + "&openid=" + openid + "&lang=zh_CN"
    response = urllib2.urlopen(user_url)
    html = response.read().decode("utf-8")
    print html
    userinfo = json.loads(html)
    print userinfo
    if "errcode" in userinfo:
        logger.debug("errcode:" + html)
        return ""
    else:
        return userinfo


def query_groups_access_token(access_token):
    queryMenuUrl = "https://api.weixin.qq.com/cgi-bin/groups/get?access_token=" + access_token
    response = urllib2.urlopen(queryMenuUrl)
    html = response.read().decode("utf-8")
    # tokeninfo = json.loads(html,ensure_ascii=False)
    tokeninfo = json.loads(html)
    return tokeninfo


def get_user_list_access_token(access_token):
    user_url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token=" + access_token
    response = urllib2.urlopen(user_url)
    html = response.read().decode("utf-8")
    print html
    userinfo = json.loads(html)
    if "errcode" in userinfo:
        logger.debug("errcode:" + html)
        return ""
    else:
        return userinfo


def create_user_group_access_token(groupname, access_token):
    interface_url = "https://api.weixin.qq.com/cgi-bin/groups/create?access_token=" + access_token
    post_data = {
        "group": {
            "name": groupname
        }
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


def modify_user_group_access_token(groupid, groupname, access_token):
    interface_url = "https://api.weixin.qq.com/cgi-bin/groups/update?access_token=" + access_token
    post_data = {
        "group": {
            "id": groupid,
            "name": groupname
        }
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


def delete_user_group_access_token(groupid, access_token):
    interface_url = "https://api.weixin.qq.com/cgi-bin/groups/delete?access_token=" + access_token
    post_data = {
        "group": {
            "id": groupid
        }
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    delete_group_result = json.loads(html)
    print delete_group_result
    return delete_group_result


def update_user_group_access_token(openid, groupid, access_token):
    interface_url = "https://api.weixin.qq.com/cgi-bin/groups/members/update?access_token=" + access_token
    post_data = {
        "openid": openid,
        "to_groupid": groupid
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    update_user_group_result = json.loads(html)
    print update_user_group_result
    return update_user_group_result


def batch_update_user_group_access_token(openids, groupid, access_token):
    interface_url = "https://api.weixin.qq.com/cgi-bin/groups/members/batchupdate?access_token=" + access_token
    post_data = {
        "openid_list": openids,  # openids　数组 最大５０;
        "to_groupid": groupid
    }
    data = json.dumps(post_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(interface_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    batch_update_user_group_result = json.loads(html)
    print batch_update_user_group_result
    return batch_update_user_group_result


def create_auth_url_access_token(redirect_url, scope, appid, component_appid):
    url = {}
    url["redirect_uri"] = redirect_url
    urlInfo = urllib.urlencode(url)
    auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + appid + '&' + urlInfo + '&response_type=code&scope=' + scope + '&state=STATE&component_appid=' + component_appid + '#wechat_redirect'
    # auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self._appid + '&' + urlInfo + '&response_type=code&scope=' + scope + '&state=1234#wechat_redirect'
    print urlInfo
    print auth_url
    return auth_url

def get_useropenid_code_access_token(code, appid, component_appid, component_access_token):
    url = "https://api.weixin.qq.com/sns/oauth2/component/access_token?appid="+appid+"&code="+code+"&grant_type=authorization_code&component_appid="+component_appid+"&component_access_token="+component_access_token
    response = urllib2.urlopen(url)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    return tokeninfo

class user_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    def create_auth_url(self, redirect_url, scope):
        # urlObj = {}
        url = {}
        url["redirect_uri"] = redirect_url
        urlInfo = urllib.urlencode(url)
        # urlObj["appid"] = self._appid
        # urlObj["redirect_uri"] = redirect_url
        # urlObj["response_type"] = "code"
        # urlObj["scope"] = scope
        # urlObj["state"] = "STATE#wechat_redirect"
        # bizString = self.formatBizQueryParaMap(urlObj, True)
        # print bizString
        # return "https://open.weixin.qq.com/connect/oauth2/authorize?"+bizString
        # redirecturl = (redirect_url)
        auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self._appid + '&' + urlInfo + '&response_type=code&scope=' + scope + '&state=1234#wechat_redirect'
        print urlInfo
        print auth_url
        return auth_url

    def formatBizQueryParaMap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = urllib.quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def get_useropenid_code(self, code):
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=" + self._appid + "&secret=" + self._appsercret + "&code=" + code + "&grant_type=authorization_code"
        response = urllib2.urlopen(url)
        html = response.read().decode("utf-8")
        # tokeninfo = json.loads(html,ensure_ascii=False)
        tokeninfo = json.loads(html)

        return tokeninfo

    def query_groups(self):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return query_groups_access_token(accessToken)

    def get_user_detailinfo(self, openid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return get_user_detailinfo_access_token(openid, access_token)

    def get_user_list(self):
        # https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return get_user_list_access_token(access_token)

    def create_user_group(self, groupname):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        logger.debug("create_user_group_access_token:" + access_token)
        print access_token
        return create_user_group_access_token(groupname, access_token)

    def modify_user_group(self, groupid, groupname):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        logger.debug("modify_user_group_access_token:" + access_token)
        return modify_user_group_access_token(groupid, groupname, access_token)

    def delete_user_group(self, groupid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        logger.debug("delete_user_group_access_token:" + access_token)
        return delete_user_group_access_token(groupid, access_token)

    def update_user_group(self, openid, groupid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        logger.debug("update_user_group_access_token:" + access_token)
        return update_user_group_access_token(openid, groupid, access_token)

    def batch_update_user_group(self, openids, groupid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        logger.debug("batch_update_user_group_access_token:" + access_token)
        return batch_update_user_group_access_token(openids, groupid, access_token)


class user_manager_open:
    def create_auth_url_component(self, appid, redirect_url, scope, component_appid):
        url = {}
        url["redirect_uri"] = redirect_url
        urlInfo = urllib.urlencode(url)
        auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + appid + '&' + urlInfo + '&response_type=code&scope=' + scope + '&state=state&component_appid=' + component_appid + '#wechat_redirect'
        print urlInfo
        print auth_url
        return auth_url

    def get_useropenid_code_component(self, code, appid, component_appid, component_access_token):
        url = "https://api.weixin.qq.com/sns/oauth2/component/access_token?appid=" + appid + "&code=" + code + "&grant_type=authorization_code&component_appid=" + component_appid + "&component_access_token=" + component_access_token
        response = urllib2.urlopen(url)
        html = response.read().decode("utf-8")
        tokeninfo = json.loads(html)
        return tokeninfo
