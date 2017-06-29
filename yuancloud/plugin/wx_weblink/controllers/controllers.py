# -*- coding: utf-8 -*-
from yuancloud import http
from yuancloud.addons.website_links.controller.main import Website_Url as weblink
from yuancloud.addons.link_tracker.controller.main import link_tracker as linktracker
from yuancloud.http import request
from yuancloud import http, SUPERUSER_ID
from yuancloud.http import request
from yuancloud.api import Environment
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import wx_public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import js_sign
import urlparse
import logging
import werkzeug

try:
    import simplejson as json
except ImportError:
    import json

_logger = logging.getLogger(__name__)


class wx_weblink(http.Controller):
    @http.route('/weixin/share', auth='none', csrf=False)
    def getshareinfo(self, **post):
        ip = request.httprequest.remote_addr
        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.environ:
            ip = request.httprequest.environ['HTTP_X_FORWARDED_FOR']
        parmsdata = request.params
        code = parmsdata['code']
        request.env['link.tracker.share'].add_click(code, ip,
                                                    request.session['geoip'].get('country_code'), stat_id=False)
        result = {}
        result.update({
            "result": True
        })
        _logger.info("执行结果:" + json.dumps(result))
        return json.dumps(result)

    @http.route('/weixin/code', auth='none', csrf=False)
    def getinfo(self, **post):
        print post
        cr, uid, context = request.cr, request.uid, request.context
        env = Environment(cr, SUPERUSER_ID, context)
        parmsdata = request.params
        code = parmsdata['code']
        link_tracker = env['link.tracker.code'].search([('code', '=', code)])
        if link_tracker:
            result = {}
            base_url = env['ir.config_parameter'].get_param('web.base.url')
            info_url = "/web/image?model=link.tracker&id=" + str(link_tracker[0]['link_id'].id) + "&field=share_image"
            result.update({
                'desc': link_tracker[0]['link_id'].share_desc,
                'title': link_tracker[0]['link_id'].title,
                'imageurl': urlparse.urljoin(base_url, info_url),
                'success': True
            })
            print result
            _logger.info(json.dumps(result))
            return json.dumps(result)
        else:
            return {}

    @http.route(['/weixin/gensign'], auth='none', csrf=False)
    def gen_sign(self, **post):
        print post
        cr, uid, context = request.cr, request.uid, request.context
        env = Environment(cr, SUPERUSER_ID, context)
        parmsdata = request.params
        code = parmsdata['code']
        url = parmsdata['url']
        try:
            officalaccount = ""
            link_tracker = env['link.tracker.code'].search([('code', '=', code)])
            if link_tracker:
                officalaccount = link_tracker[0]['link_id']['officialaccount']
            # officalaccount = env['wx.officialaccount'].search(['|',('wx_appid', '=', app_id),('id', '=', int(app_id) if app_id.isdigit() else -1)])[0]
            print officalaccount
        except:
            officalaccount = ""
        print officalaccount
        if officalaccount:
            sign_info = self.exec_signature(url, officalaccount)
            print sign_info
            return json.dumps(sign_info)
        else:
            return {}

    def exec_signature(self, url, officalaccount):
        app_id = officalaccount['wx_appid']
        app_sercert = officalaccount['wx_appsecret']
        public_sdk = wx_public_sdk.wx_public_sdk(app_id, app_sercert)
        js_api_ticket = public_sdk.get_jsapi_ticket()
        print js_api_ticket
        jssign = js_sign.js_sign(js_api_ticket, url)
        result = jssign.gen_js_sign()
        result['appid'] = app_id
        print result
        return (result)


class WxWeblink(weblink):
    @http.route()
    def create_shorten_url(self, **post):
        print post
        if 'url' not in post or post['url'] == '':
            return {'error': 'empty_url'}
        return request.env['link.tracker'].create(post).read()


class link_tracker(linktracker):
    @http.route()
    def full_url_redirect(self, code, **post):
        ip = request.httprequest.remote_addr
        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.environ:
            ip = request.httprequest.environ['HTTP_X_FORWARDED_FOR']
        request.env['link.tracker.click'].add_click(code, ip, request.session['geoip'].get('country_code'),
                                                    stat_id=False)
        redirect_url = request.env['link.tracker'].get_url_from_code(code)
        return werkzeug.utils.redirect(redirect_url or '', 301)
