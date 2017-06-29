# -*- coding: utf-8 -*-

import logging
try:
    import simplejson as json
except ImportError:
    import json
from yuancloud import models, fields, api, _
import uuid


_logger = logging.getLogger(__name__)


class base_apppartner(models.Model):
    _name = 'base.apppartner'

    key = fields.Char(string='关键字', required=True, readonly=True, default=lambda self: uuid.uuid4())
    user = fields.Many2one('res.users', '用户')
    apppartner_type = fields.Selection(
        [('officalaccount', '微信公众号'), ('enterpriseaccount', '微信企业号应用'),('third_platform','微信第三方平台'), ('youzan', '有赞平台'),
         ('taobao', '淘宝平台')], string="接入平台类型")
    officalaccount=fields.Many2one('wx.officialaccount',string="微信公众号")
    enterpriseaccount=fields.Many2one('wx.officialaccount',string="微信企业号应用")
    third_platform=fields.Many2one('wx.third_platform',string="微信第三方平台")
    apppartner_desc=fields.Text("备注")

