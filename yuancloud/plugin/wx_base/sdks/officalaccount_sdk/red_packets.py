# -*- coding: utf-8 -*-
import urllib2
import urllib
import hashlib
import collections
import ssl
import httplib
import json
import logging
import time
import datetime
import random
import string
import os
from yuancloud.http import request
from yuancloud.addons.wx_base.models import util

_logger = logging.getLogger(__name__)

def to_tag(k, v):
    return '<{key}>{value}</{key}>'.format(key=k, value=get_content(k, v))


def get_content(k, v):
    if isinstance(v, basestring):
        # it's a string, so just return the value
        return unicode(v).encode('utf-8')
    elif isinstance(v, dict):
        # it's a dict, so create a new tag for each element
        # and join them with newlines
        return '\n%s\n' % '\n'.join(to_tag(*e) for e in v.items())
    elif isinstance(v, list):
        # it's a list, so create a new key for each element
        # by using the enumerate method and create new tags
        return '\n%s\n' % '\n'.join(to_tag('{key}-{value}'.format(key=k, value=i + 1), e) for i, e in enumerate(v))

CERT_FILE = 'apiclient_cert.pem'  # Renamed from PEM_FILE to avoid confusion
KEY_FILE = 'apiclient_key.pem'  # This is your client cert!


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):

    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

def getbody(data):
    mch_key=data['key']
    del data['key']
    _, prestr = util.params_filter(data)
    print prestr
    print mch_key
    data['sign'] = util.build_mysign(prestr, mch_key, 'MD5')
    data_xml = "<xml>" + (util.json2xml(data)) + "</xml>"
    print data_xml
    return data_xml

def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join([random.choice(chars) for n in xrange(size)])

#发放普通现金红包
def send_redpocket(mch_billno,mch_id,mch_key,appid,send_name,openid,total_amount,total_num,wishing,client_ip,act_name,remark):
    #key_file = os.path.join(request.httprequest.host_url,
    #                                     "ycloud_wx/static/cert/"+mch_id+"/apiclient_key.pem")
    #cert_file= os.path.join(request.httprequest.host_url,
    #                                     "ycloud_wx/static/cert/"+mch_id+"/apiclient_cert.pem")
    cert_file = os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_cert.pem')
    print cert_file
    key_file= os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_key.pem')
    print key_file
    cert_handler = HTTPSClientAuthHandler(key_file, cert_file)
    opener = urllib2.build_opener(cert_handler)
    urllib2.install_opener(opener)
    try:
        data = {}
        data.update({
                "nonce_str":random_generator(),
                "mch_billno":mch_billno,
                "mch_id":mch_id,
                "wxappid":appid,
                "send_name":send_name,
                "re_openid":openid,
                "total_amount":total_amount,
                "total_num":total_num,
                "wishing":wishing,
                "client_ip":client_ip,
                "act_name":act_name,
                "remark":remark,
                "key":mch_key
            })
        print data
        req = urllib2.Request("https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack",
                                  data=getbody(data), headers={'Content-Type': 'application/xml'})
        u = urllib2.urlopen(req)
        response = u.read()
        _logger.info(response)
        return response
    except Exception as e:
        _logger.error("发送红包出错:"+str(e))

#发送裂变红包
def send_groupredpacket(mch_billno,mch_id,mch_key,appid,send_name,openid,total_amount,total_num,wishing,act_name,remark):
    url="https://api.mch.weixin.qq.com/mmpaymkttransfers/sendgroupredpack"
    cert_file = os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_cert.pem')
    print cert_file
    key_file= os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_key.pem')
    print key_file
    cert_handler = HTTPSClientAuthHandler(key_file, cert_file)
    opener = urllib2.build_opener(cert_handler)
    urllib2.install_opener(opener)
    try:
        data = {}
        data.update({
                "nonce_str":random_generator(),
                "mch_billno":mch_billno,
                "mch_id":mch_id,
                "wxappid":appid,
                "send_name":send_name,
                "re_openid":openid,
                "total_amount":total_amount,
                "total_num":total_num,
                "amt_type":"ALL_RAND",
                "wishing":wishing,
                "act_name":act_name,
                "remark":remark,
                "key":mch_key
            })
        print data
        req = urllib2.Request(url,
                                  data=getbody(data), headers={'Content-Type': 'application/xml'})
        u = urllib2.urlopen(req)
        response = u.read()
        _logger.info(response)
        return response
    except Exception as e:
        _logger.error("发送裂变红包出错:"+str(e))


#企业付款接口
def send_promotion_transfer(mch_appid,mch_id,partner_trade_no,openid,check_name,re_user_name,amount,desc,spbill_create_ip):
    url="https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
    cert_file = os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_cert.pem')
    print cert_file
    key_file= os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_key.pem')
    print key_file
    cert_handler = HTTPSClientAuthHandler(key_file, cert_file)
    opener = urllib2.build_opener(cert_handler)
    urllib2.install_opener(opener)
    try:
        data = {}
        data.update({
                "nonce_str":random_generator(),
                "mch_billno":partner_trade_no,
                "mch_id":mch_id,
                "mch_appid":mch_appid,
                "check_name":check_name,
                "re_openid":openid,
                "re_user_name":re_user_name,
                "amount":amount,
                "desc":desc,
                "spbill_create_ip":spbill_create_ip
            })
        print data
        req = urllib2.Request(url,data=getbody(data), headers={'Content-Type': 'application/xml'})
        u = urllib2.urlopen(req)
        response = u.read()
        _logger.info(response)
        return response
    except Exception as e:
        _logger.error("调用企业付款接口出错:"+str(e))

def send_coupon(coupon_stock_id,partner_trade_no,openid,appid,mch_id):
    url="https://api.mch.weixin.qq.com/mmpaymkttransfers/send_coupon"
    cert_file = os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_cert.pem')
    print cert_file
    key_file= os.path.join(os.path.dirname(__file__), '../static/cert/'+mch_id+'/apiclient_key.pem')
    print key_file
    cert_handler = HTTPSClientAuthHandler(key_file, cert_file)
    opener = urllib2.build_opener(cert_handler)
    urllib2.install_opener(opener)
    try:
        data = {}
        data.update({
                "nonce_str":random_generator(),
                "openid_count":1,
                "coupon_stock_id":coupon_stock_id,
                "partner_trade_no":partner_trade_no,
                "openid":openid,
                "appid":appid,
                "re_openid":openid,
                "mch_id":mch_id
            })
        print data
        req = urllib2.Request(url,data=getbody(data), headers={'Content-Type': 'application/xml'})
        u = urllib2.urlopen(req)
        response = u.read()
        _logger.info(response)
        return response
    except Exception as e:
        _logger.error("发送代金劵接口出错:"+str(e))


