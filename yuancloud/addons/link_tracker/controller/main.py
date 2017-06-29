# -*- coding: utf-8 -*-
import werkzeug

from yuancloud.addons.web import http
from yuancloud.http import request


class link_tracker(http.Controller):
    @http.route('/r/<string:code>', type='http', auth='none', website=True)
    def full_url_redirect(self, code, **post):
        request.env['link.tracker.click'].add_click(code, request.httprequest.environ['HTTP_X_FORWARDED_FOR'], request.session['geoip'].get('country_code'), stat_id=False)
        redirect_url = request.env['link.tracker'].get_url_from_code(code)
        return werkzeug.utils.redirect(redirect_url or '', 301)
