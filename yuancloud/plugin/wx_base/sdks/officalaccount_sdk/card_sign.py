# -*- coding: utf-8 -*-
import time
import os
import urllib2,json,urllib
import logging
import random
import string
import hashlib

class card_sign:

    def __init__(self,card_api_ticket,app_id,card_id,card_type='',shopId=''):
        self.ret = {
            'nonce_str': self.create_nonce_str(),
            'api_ticket': card_api_ticket,
            'timestamp': str(self.create_timestamp()),
            'card_id':card_id,
            'location_id':shopId,
            'card_type':card_type,
            'app_id':app_id
        }

    def create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def create_timestamp(self):
        return int(time.time())

    def gen_sign(self):
        result=""
        for keyinfo in sorted(self.ret.iteritems(), key = lambda asd:asd[1]):
            print keyinfo
            result=result+str(keyinfo[1])
        info = ''.join(['%s' % (keyvaule[1]) for keyvaule in sorted(self.ret.iteritems(), key = lambda asd:asd[1])])
        print result
        print info
        self.ret['signature'] = hashlib.sha1(result).hexdigest()
        return self.ret

class add_card_sign:

    def __init__(self,card_api_ticket,card_id,openid='',code=''):
        self.ret = {
            'nonce_str': self.create_nonce_str(),
            'api_ticket': card_api_ticket,
            'timestamp': str(self.create_timestamp()),
            'card_id':card_id
        }
        if openid<>'':
            self.ret['openid']=openid
        if code<>'':
            self.ret['code']=code


    def create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def create_timestamp(self):
        return int(time.time())

    def gen_sign(self):
        result=""
        for keyinfo in sorted(self.ret.iteritems(), key = lambda asd:asd[1]):
            print keyinfo
            result=result+str(keyinfo[1])
        info = ''.join(['%s' % (keyvaule[1]) for keyvaule in sorted(self.ret.iteritems(), key = lambda asd:asd[1])])
        print result
        print info
        self.ret['signature'] = hashlib.sha1(result).hexdigest()
        return self.ret

class edit_address_sign:
    def __init__(self,appId,url,access_token):
        self.ret = {
            'noncestr': "123456",#str(self.create_nonce_str()),
            'appId': str(appId),
            'timeStamp': "1384841012",#str(self.create_timestamp()),
            'url':str(url),
            'accessToken':str(access_token)
        }
    def create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def create_timestamp(self):
        return str(int(time.time()))

    def gen_address_sign(self):
        print self.ret
        string = '&'.join(['%s=%s' % (key.lower(), (self.ret[key])) for key in sorted(self.ret)])
        print string
        self.ret['addrsign'] = hashlib.sha1(string).hexdigest()
        print self.ret
        return self.ret

