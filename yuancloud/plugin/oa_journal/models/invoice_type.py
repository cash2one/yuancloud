# -*- coding: utf-8 -*-
from yuancloud import models, fields, api

class invocie_type(models.Model):
    '''
    模型：发票类型（档案），
    使用者：日常流水
    '''
    _name = 'oa_journal.invoice.type'
    _description = 'OA Journal Invoice Type'
    name = fields.Char(string='发票类型',required=True)
    active = fields.Boolean(string='生效',help='不生效时，将不显示')
    note = fields.Text(string='备注')
    invoicing_method = fields.Selection([('simple', '没分组'), ('grouped', '已分组')], '开票方式', required=True)