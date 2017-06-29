# -*- coding: utf-8 -*-
from yuancloud.http import request
from yuancloud.osv import orm


class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def get_utm_domain_cookies(self):
        return request.httprequest.host

    def _dispatch(self):
        response = super(ir_http, self)._dispatch()
        for var, dummy, cook in self.pool['utm.mixin'].tracking_fields():
            if var in request.params and request.httprequest.cookies.get(var) != request.params[var]:
                try:
                    response.set_cookie(cook, request.params[var], domain=self.get_utm_domain_cookies())
                except:
                    pass
        return response
