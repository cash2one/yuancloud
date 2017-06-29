# -*- coding: utf-8 -*-
import time
import os
import urllib2,json,urllib
import logging
import random
import string
import hashlib

class js_sign:

    def __init__(self,jsapi_ticket,url):
        self.ret = {
            'nonceStr': self.create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.create_timestamp(),
            'url':url
        }

    def create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def create_timestamp(self):
        return int(time.time())

    def gen_js_sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret
