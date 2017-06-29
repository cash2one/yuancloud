# -*- coding: utf-8 -*-
from yuancloud import http
from yuancloud.addons.website_links.controller.main import Website_Url as weblink
from yuancloud.http import request
from yuancloud import http, SUPERUSER_ID
from yuancloud.http import request
from yuancloud.api import Environment
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import wx_public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import js_sign
import logging
import os
import sys
import jinja2
import simplejson
import werkzeug.utils
import werkzeug.wrappers

try:
    import simplejson as json
except ImportError:
    import json
import urlparse
from urllib import urlencode

_logger = logging.getLogger(__name__)

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('yuancloud.addons.wx_weblink', "views")

env2 = jinja2.Environment(loader=loader, autoescape=True)
env2.filters["json"] = simplejson.dumps


class ShareTimeLine(http.Controller):
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

    @http.route('/weixin/friendshare', auth='none', crsf=False)
    def friendshare(self, **post):
        page = 'wx_weblink.shareinfo'
        values = {}
        cr, uid, context = request.cr, request.uid, request.context
        env = Environment(cr, SUPERUSER_ID, context)
        parmsdata = request.params
        if 'code' not in parmsdata:
            return request.website.render('website.404')
        code = parmsdata['code']
        link_tracker = env['link.tracker.code'].search([('code', '=', code)])
        if link_tracker:
            sign_info = {}
            url = request.httprequest.url
            print url
            # try:
            #     officalaccount = ""
            #     link_tracker = env['link.tracker.code'].search([('code', '=', code)])
            #     if link_tracker:
            #         officalaccount = link_tracker[0]['link_id']['officialaccount']
            #     print officalaccount
            # except:
            #     officalaccount = ""
            # print officalaccount
            officalaccount = link_tracker[0]['link_id']['officialaccount']
            if officalaccount:
                sign_info = self.exec_signature(url, officalaccount)
                print sign_info
            else:
                sign_info = {}
            base_url = env['ir.config_parameter'].get_param('web.base.url')
            info_url = "/web/image?model=link.tracker&id=" + str(link_tracker[0]['link_id'].id) + "&field=share_image"
            # 总点击量:
            if link_tracker[0]['link_id'].share_mood_1:
                share_mood_1 = link_tracker[0]['link_id'].share_mood_1
            else:
                share_mood_1 = ""
            print share_mood_1
            if link_tracker[0]['link_id'].share_mood_2:
                share_mood_2 = link_tracker[0]['link_id'].share_mood_2
            else:
                share_mood_2 = ""
            print share_mood_2
            if link_tracker[0]['link_id'].share_mood_3:
                share_mood_3 = link_tracker[0]['link_id'].share_mood_3
            else:
                share_mood_3 = ""
            print share_mood_3
            values.update({
                'desc': link_tracker[0]['link_id'].share_desc,
                'title': link_tracker[0]['link_id'].title,
                'share_mood_1': share_mood_1,
                'share_mood_2': share_mood_2,
                'share_mood_3': share_mood_3,
                'imageurl': urlparse.urljoin(base_url, info_url),
                "signature": json.dumps(sign_info)
            })
            return request.render(page, values)
        else:
            return request.website.render('website.404')

    @http.route('/weixin/lottery', auth='none', csrf=False)
    def lottery(self, **post):
        return env2.get_template("lottery.html").render({

        })

    @http.route('/weixin/index', auth='none', csrf=False)
    def lottery(self, **post):
        return env2.get_template("index.html").render({

        })

    @http.route('/weixin/sharke', auth='none', csrf=False)
    def sharke(self, **post):
        return env2.get_template("sharke_index.html").render({

        })

    @http.route('/weixin/dy', auth='none', csrf=False)
    def dy(self, **post):
        return env2.get_template("dy.html").render({

        })

    @http.route('/weixin/finish', auth='none', csrf=False)
    def finish(self, **post):
        return env2.get_template("finish.html").render({

        })

    @http.route('/weixin/sharetimeline', auth='none', csrf=False)
    def sharetimeline_real(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        env = Environment(cr, SUPERUSER_ID, context)
        parmsdata = request.params
        code = parmsdata['code']
        link_tracker = env['link.tracker.code'].search([('code', '=', code)])
        if link_tracker:
            sign_info = {}
            url = request.httprequest.url
            print url
            # try:
            #     officalaccount = ""
            #     link_tracker = env['link.tracker.code'].search([('code', '=', code)])
            #     if link_tracker:
            #
            #     print officalaccount
            # except:
            #     officalaccount = ""
            # print officalaccount
            officalaccount = link_tracker[0]['link_id']['officialaccount']
            if officalaccount:
                sign_info = self.exec_signature(url, officalaccount)
                print sign_info
            else:
                sign_info = {}
            base_url = env['ir.config_parameter'].get_param('web.base.url')
            info_url = "/web/image?model=link.tracker&id=" + str(link_tracker[0]['link_id'].id) + "&field=share_image"
            if link_tracker[0]['link_id'].share_mood_1:
                share_mood_1 = link_tracker[0]['link_id'].share_mood_1
            else:
                share_mood_1 = ""
            print share_mood_1
            if link_tracker[0]['link_id'].share_mood_2:
                share_mood_2 = link_tracker[0]['link_id'].share_mood_2
            else:
                share_mood_2 = ""
            print share_mood_2
            if link_tracker[0]['link_id'].share_mood_3:
                share_mood_3 = link_tracker[0]['link_id'].share_mood_3
            else:
                share_mood_3 = ""
            print share_mood_3
            return env2.get_template("sharetimeline.html").render({
                'desc': link_tracker[0]['link_id'].share_desc,
                'title': link_tracker[0]['link_id'].title,
                'share_mood_1': share_mood_1,
                'share_mood_2': share_mood_2,
                'share_mood_3': share_mood_3,
                'imageurl': urlparse.urljoin(base_url, info_url),
                "signature": json.dumps(sign_info)
            })

    @http.route('/weixin/sharetime/<id>', auth='none', csrf=False)
    def shareTimeline(self, **post):
        print post
        cr, uid, context = request.cr, request.uid, request.context
        env = Environment(cr, SUPERUSER_ID, context)
        id = post['id']
        link_new = env['link.tracker'].sudo().search([('id', '=', id)])
        if link_new:
            link_tracker = env['link.tracker.code'].search([('link_id', '=', link_new.id)])
            if link_tracker:
                currenturl = request.httprequest.url
                base_url = env['ir.config_parameter'].get_param('web.base.url')
                # utms = {}
                # utms['redirect']=link_new.short_url
                # utms['code']=link_tracker.code
                # info_url = "/weixin/sharetimeline?"+urlencode(utms)
                # #currenturl=urlparse.urljoin(base_url, info_url)
                # currenturl='%s?%s' %(base_url,)
                parsed = urlparse.urlparse(currenturl)
                utms = {}
                utms['redirect'] = link_new.short_url
                utms['code'] = link_tracker.code
                print parsed.netloc
                print parsed.path
                redirected_url = '%s://%s%s?%s&%s#%s' % (
                parsed.scheme, parsed.netloc, '/weixin/friendshare', urlencode(utms), parsed.query, parsed.fragment)
                print redirected_url
                _logger.info("redirected_url:"+redirected_url)
                return werkzeug.utils.redirect(redirected_url or '', 301)
