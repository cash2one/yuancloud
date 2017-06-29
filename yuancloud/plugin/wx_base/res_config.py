# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

from yuancloud.osv import osv, fields

import logging
_logger = logging.getLogger(__name__)

class base_config_settings(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'module_wx_base': fields.boolean('微信基类...'),
    }
