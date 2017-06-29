# -*- coding: utf-8 -*-
from yuancloud import models, fields, api

class account_move(models.Model):
    '''
    功能：记账凭证（分类账条目），扩展“附件张数”字段
    '''
    _inherit = 'account.move'
    attachment_count=fields.Integer(string='附件张数')
