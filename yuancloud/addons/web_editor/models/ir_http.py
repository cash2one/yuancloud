# -*- coding: utf-8 -*-
from yuancloud.osv import orm
from yuancloud.http import request


class ir_http(orm.AbstractModel):
    _inherit = 'ir.http'

    def _dispatch(self):
        if 'editable' in request.httprequest.args and 'editable' not in request.context:
            request.context['editable'] = True
        if 'edit_translations' in request.httprequest.args and 'edit_translations' not in request.context:
            request.context['edit_translations'] = True
        if request.context.get('lang') != "en_US" and 'translatable' not in request.context:
            request.context['translatable'] = True
        return super(ir_http, self)._dispatch()
