# -*- coding: utf-8 -*-
from yuancloud import  http
import threading
import sys
from yuancloud import cache
reload(sys)
sys.setdefaultencoding('utf-8')
from yuancloud.api import Environment
import os
import sys
import jinja2
import random
import time
from yuancloud import http, SUPERUSER_ID

try:
    import simplejson as json
except ImportError:
    import json

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('yuancloud.addons.diy_whm', "views")

env_jinjia = jinja2.Environment(loader=loader, autoescape=True)
env_jinjia.filters["json"] = json.dumps


class bianmin(http.Controller):

    @http.route('/whm/bianmin_info',auth='none',csrf=False)
    def display_bianmin_info(self,**kw):
        '''
        功能：便民信息
        :param kw:
        :return:
        '''
        return env_jinjia.get_template("bianmin.html").render({
        })