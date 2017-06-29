# -*- coding: utf-8 -*-
import time
import os
import urllib2,json,urllib
import logging
from yuancloud import cache
from yuancloud.osv import fields, osv, expression
from yuancloud.tools.translate import _

logger = logging.getLogger(__name__)

def get_authorizer_access_token(appid,component_appid,component_sercret,refresh_token):
    key=component_appid+"ticket"
    ticket=cache.redis.get(key)
    publicsdk=public_sdk(component_appid,component_sercret)
    return publicsdk.api_authorizer_token(ticket,appid,refresh_token)

class public_sdk:

    def __init__(self,AppId,AppSercret):
        self._appid=AppId
        self._appSercret=AppSercret

    def get_api_component_token(self,ticket_value):
        key=self._appid+"component_access_token"
        token =cache.redis.get(key)
        if token == None:
            category_url="https://api.weixin.qq.com/cgi-bin/component/api_component_token"
            category_data={
                "component_appid":self._appid,
                "component_appsecret": self._appSercret,
                "component_verify_ticket": ticket_value
                }
            req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
            req.add_header("Content-Type","application/json")
            response=urllib2.urlopen(req)
            html = response.read().decode("utf-8")
            logger.debug('html:'+html)
            tokeninfo = json.loads(html)
            print tokeninfo
            if "errcode" not in tokeninfo:
                token=tokeninfo["component_access_token"]
                cache.redis.set(key, token,7200)
            else:
                raise osv.except_osv(_('Error!'),_('获取component_access_token出错'))
                #return "获取component_access_token出错:"+str(tokeninfo['errcode'])
        return token

    def get_api_create_preauthcode(self,ticket_value):
        key=self._appid+"preauthcode"
        token =cache.redis.get(key)
        if token == None:
            access_token=self.get_api_component_token(ticket_value)
            category_url="https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode?component_access_token="+access_token
            category_data={
                "component_appid":self._appid
                }
            req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
            req.add_header("Content-Type","application/json")
            response=urllib2.urlopen(req)
            html = response.read().decode("utf-8")
            logger.debug('html:'+html)
            tokeninfo = json.loads(html)
            print tokeninfo
            if "errcode" not in tokeninfo:
                token=tokeninfo["pre_auth_code"]
                cache.redis.set(key, token,600)
                return  token
            else:
                return "获取pre_auth_code出错:"+str(tokeninfo['errcode'])
        return token

    def api_query_auth(self,authorization_code,ticket_value):
        access_token=self.get_api_component_token(ticket_value)
        category_url="https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token="+access_token
        category_data={
            "component_appid":self._appid ,
            "authorization_code": authorization_code
            }
        req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type","application/json")
        response=urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:'+html)
        tokeninfo = json.loads(html)
        print tokeninfo
        return tokeninfo

    def api_authorizer_token(self,ticket_value,auth_appid_value,refresh_token_value):
        key=auth_appid_value+"authorizer_access_token"
        token =cache.redis.get(key)
        if token==None:
            access_token=self.get_api_component_token(ticket_value)
            category_url="https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token?component_access_token="+access_token
            category_data={
                "component_appid":self._appid,
                "authorizer_appid":auth_appid_value,
                "authorizer_refresh_token":refresh_token_value
                }
            print category_data
            req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
            req.add_header("Content-Type","application/json")
            response=urllib2.urlopen(req)
            html = response.read().decode("utf-8")
            logger.debug('html:'+html)
            tokeninfo = json.loads(html)
            print tokeninfo
            if "errcode" not in tokeninfo:
                token=tokeninfo["authorizer_access_token"]
                cache.redis.set(key, token,7200)
            else:
                raise osv.except_osv(_('Error!'),_('获取authorizer_access_token出错'))
        else:
            return token

    def api_get_authorizer_info(self,auth_appid_value,ticket_value):
        access_token=self.get_api_component_token(ticket_value)
        category_url="https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info?component_access_token="+access_token
        category_data={
            "component_appid":self._appid,
            "authorizer_appid": auth_appid_value
            }
        req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type","application/json")
        response=urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:'+html)
        tokeninfo = json.loads(html)
        print tokeninfo
        return tokeninfo

    def api_get_authorizer_option(self,auth_appid_value,option_name_value,ticket_value):
        access_token=self.get_api_component_token(ticket_value)
        category_url="https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_option?component_access_token="+access_token
        category_data={
            "component_appid":self._appid,
            "authorizer_appid": auth_appid_value,
            "option_name": option_name_value
            }
        req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type","application/json")
        response=urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:'+html)
        tokeninfo = json.loads(html)
        print tokeninfo
        return tokeninfo

    def api_set_authorizer_option(self,auth_appid_value,option_name_value,option_value_value,ticket_value):
        access_token=self.get_api_component_token(ticket_value)
        category_url="https://api.weixin.qq.com/cgi-bin/component/api_set_authorizer_option?component_access_token="+access_token
        category_data={
            "component_appid":self._appid,
            "authorizer_appid": auth_appid_value,
            "option_name": option_name_value,
            "option_value":option_value_value
            }
        req=urllib2.Request(category_url,json.dumps(category_data,ensure_ascii=False).encode('utf8'))
        req.add_header("Content-Type","application/json")
        response=urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        logger.debug('html:'+html)
        tokeninfo = json.loads(html)
        print tokeninfo
        return tokeninfo