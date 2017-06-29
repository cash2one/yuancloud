# -*- coding: utf-8 -*-
import time
import os
import logging
import sys
from yuancloud.addons.wx_base.models import util

import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)

class bill_manager:
    def downloadbill(self,values):
        try:
            appid = values['appid']
            mch_id = values['mch_id']
            mch_secret=values['mch_secret']
            bill_type='ALL'
            bill_date=time.strftime('%Y%m%d',time.localtime(time.time()))
            if 'bill_type' in values:
                bill_type=values['bill_type']
            if 'bill_date' in values:
                bill_date=values['bill_date'].replace('-','')
            nonce_str = util.random_generator()
            data_post = {}
            data_post.update(
                       {
                           'appid': appid,
                           'mch_id': mch_id,
                           'nonce_str': nonce_str,
                           'bill_type': bill_type,
                           'bill_date': bill_date
                       }
                   )
            _, prestr = util.params_filter(data_post)
            sign = util.build_mysign(prestr, mch_secret, 'MD5')
            data_post['sign'] = sign
            data_xml = "<xml>" + util.json2xml(data_post) + "</xml>"
            url = 'https://api.mch.weixin.qq.com/pay/downloadbill'
            request = urllib2.Request(url, data_xml)
            result = util._try_url(request, tries=3)
            return result
        except Exception as e:
            _logger.error(e)

    def orderquery(self,values):
        try:
            appid = values['appid']
            mch_id = values['mch_id']
            mch_secret=values['mch_secret']
            transaction_id=values['transaction_id']
            nonce_str = util.random_generator()
            data_post = {}
            data_post.update(
                       {
                           'appid': appid,
                           'mch_id': mch_id,
                           'transaction_id':transaction_id,
                           'nonce_str': nonce_str,
                       }
                   )
            _, prestr = util.params_filter(data_post)
            sign = util.build_mysign(prestr, mch_secret, 'MD5')
            data_post['sign'] = sign
            data_xml = "<xml>" + util.json2xml(data_post) + "</xml>"
            url = 'https://api.mch.weixin.qq.com/pay/orderquery'
            request = urllib2.Request(url, data_xml)
            result = util._try_url(request, tries=3)
            return result
        except Exception as e:
            _logger.error(e)
