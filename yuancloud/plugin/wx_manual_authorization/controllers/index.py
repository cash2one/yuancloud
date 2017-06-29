# -*- coding: utf-8 -*-
from yuancloud import http
from lxml import etree
from yuancloud import SUPERUSER_ID
import main
import qy_main


class ycloudbase(http.Controller):
    @http.route(['/ycloud_base/cfg/<key>'], auth='none', csrf=False)
    def index(self, **kw):
        request = http.request
        cr = request.cr
        uid = SUPERUSER_ID
        data = http.request.httprequest.data
        key = kw['key']
        context = http.request.context
        print request.httprequest.method
        cfgModel = request.registry.get('base.apppartner')
        if cfgModel:
            # execute(self,cr,uid,key,values,context=None):
            rv_id=cfgModel.search(cr, uid,[('key','=',key)],context=context)
            #rv_id = cfgModel.search(cr, uid, [('key', '=', key)], context)
            if rv_id:
                rv = cfgModel.browse(cr, uid, rv_id[0], context)
                return self.execute(cr, uid, key, rv, data)
            return str(False)
        return str(False)

    def execute(self, cr, uid, key, rv, data):
        request = http.request
        wx_handler = main.wx_index()
        qy_handler = qy_main.qy_main_index()
        if request.httprequest.method == 'GET':
            if rv['apppartner_type'] == "enterpriseaccount":
                return qy_handler.check_server_valid(request.httprequest, rv)
            elif rv['apppartner_type'] == "officalaccount":
                return wx_handler.check_server_valid(request.httprequest, rv)
        else:
            uid = rv[0]['user']['id']
            if rv['apppartner_type'] == "enterpriseaccount":
                return qy_handler.execute_wx_qy(cr, uid, data, rv)
            elif rv['apppartner_type'] == "officalaccount":
                return wx_handler.execute_wx(cr, uid, data, rv)
