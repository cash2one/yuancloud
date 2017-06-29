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


class store(http.Controller):

    @http.route('/whm/store_info/<key>',auth='none',csrf=False)
    def display_store_info(self,**kw):
        print kw
        store_id=kw['key']
        env_new = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        store_info=env_new['o2o.store'].search([('id','=',store_id)])
        name=store_info.name
        address=store_info.address
        contact=store_info.contact
        if not contact:
            contact=''
        phone=store_info.phone
        if not phone:
            phone=''
        mobile=store_info.mobile
        if not mobile:
            mobile=''
        simple_info=store_info.simple_info
        if not simple_info:
            simple_info='暂无简介'
        recommend=store_info.recommend
        if not recommend:
            recommend=''
        category=store_info.category.name
        if not category:
            category='暂未分类'
        category_line=store_info.category_line.name
        if not category_line:
            category_line=''
        return env_jinjia.get_template("display_store.html").render({
            "name": name,
            "address": address,
            "contact": contact,
            "phone":phone,
            "mobile": mobile,
            "simple_info": simple_info,
            "recommend":recommend ,
            "category": category,
            "category_line": category_line,
        })
