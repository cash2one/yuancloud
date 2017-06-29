# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import logging
from yuancloud.osv import osv
from yuancloud.tools.translate import _

logger = logging.getLogger(__name__)


# 母商户资质申请接口
def upload_card_agent_qualification(register_capital, business_license_media_id, tax_registration_certificate_media_id,
                                    last_quarter_tax_listing_media_id, component_access_token):
    category_url = "http://api.weixin.qq.com/cgi-bin/component/upload_card_agent_qualification?access_token=" + component_access_token
    category_data = {
        "register_capital": register_capital,
        "business_license_media_id": business_license_media_id,
        "tax_registration_certificate_media_id": tax_registration_certificate_media_id,
        "last_quarter_tax_listing_media_id": last_quarter_tax_listing_media_id
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" in tokeninfo:
        if tokeninfo['errcode'] == 0:
            pass
        else:
            raise osv.except_osv(_('Error!'), _('提交母商户资质出错'))
    else:
        raise osv.except_osv(_('Error!'), _('提交母商户资质出错'))


# 母商户资质审核查询接口
def check_card_agent_qualification(component_access_token):
    url = "http://api.weixin.qq.com/cgi-bin/component/check_card_agent_qualification?access_token=" + component_access_token
    response = urllib2.urlopen(url)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if "errcode" in tokeninfo:
        return u"查询母商户资质出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


# 子商户资质提交接口
def upload_card_merchant_qualification(appid, name, logo_media_id, business_license_media_id, agreement_file_media_id,
                                       operator_id_card_media_id, primary_category_id, secondary_category_id,
                                       component_access_token):
    category_url = "http://api.weixin.qq.com/cgi-bin/component/upload_card_merchant_qualification?access_token=" + component_access_token
    category_data = {
        "appid": appid,
        "name": name,
        "logo_media_id": logo_media_id,
        "business_license_media_id": business_license_media_id,
        "agreement_file_media_id": agreement_file_media_id,
        "operator_id_card_media_id": operator_id_card_media_id,
        "primary_category_id": primary_category_id,
        "secondary_category_id": secondary_category_id
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" in tokeninfo:
        if tokeninfo['errcode'] == 0:
            pass
        else:
            raise osv.except_osv(_('Error!'), _('提交子商户资质出错'))
    else:
        raise osv.except_osv(_('Error!'), _('提交子商户资质出错'))


# 子商户资质审核查询接口
def check_card_merchant_qualification(appid, component_access_token):
    category_url = "http://api.weixin.qq.com/cgi-bin/component/check_card_merchant_qualification?access_token=" + component_access_token
    category_data = {
        "appid": appid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" in tokeninfo:
        return u"查询子商户资质出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


# 卡券开放类目查询接口
def getapplyprotocol(component_access_token):
    url = "https://api.weixin.qq.com/card/getapplyprotocol?access_token=" + component_access_token
    response = urllib2.urlopen(url)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] <> 0:
        return u"查询卡劵开放类目出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


# 拉取单个子商户信息接口
def get_card_merchant_info(appid, component_access_token):
    category_url = "http://api.weixin.qq.com/cgi-bin/component/get_card_merchant?access_token=" + component_access_token
    category_data = {
        "appid": appid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" in tokeninfo:
        return u"查询子商户信息出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


# 拉取子商户列表接口
def batchget_card_merchant(component_access_token):
    category_url = "http://api.weixin.qq.com/cgi-bin/component/batchget_card_merchant?access_token=" + component_access_token
    category_data = {
        "next": ""
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if "errcode" in tokeninfo:
        return u"拉取子商户列表出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return tokeninfo


# 确认授权
def api_confirm_authorization(component_appid, authorizer_appid, funcscope_category_id, confirm_value,
                              component_access_token):
    category_url = "https://api.weixin.qq.com/cgi-bin/component/api_confirm_authorization?component_access_token" + component_access_token
    category_data = {
        "component_appid": component_appid,
        "authorizer_appid": authorizer_appid,
        "funcscope_category_id": funcscope_category_id,
        "confirm_value": confirm_value
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode']<>0:
        return u"强制授权接口调用失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']
    else:
        return "强制授权接口调用成功"
