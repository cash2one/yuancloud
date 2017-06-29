# -*- coding: utf-8 -*-
from yuancloud import models, fields, api

class ecplatform(models.Model):
    '''
    模型：电商平台（档案），
    使用者：日常流水
    '''
    _name = 'oa_journal.ecplatform'
    _description = 'OA Journal EC Platform'
    _rec_name = 'platform_name'
    platform_code = fields.Char(string='编码',required=True)
    platform_name = fields.Char(string='名称',required=True)
    platform_url = fields.Char(string='网址')
    enabled = fields.Boolean(string='生效',default=True)