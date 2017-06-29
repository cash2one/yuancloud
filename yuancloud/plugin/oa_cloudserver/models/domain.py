# -*- coding: utf-8 -*-
# from openerp import models, fields, api
import logging

try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields

_logger = logging.getLogger(__name__)

class cloudserver_domain(models.Model):
    '''
    实体：域名管理
    '''
    _name = 'oa.cloudserver.domain'
    provider = fields.Selection([('ali', '阿里'), ('tencent', '腾讯')],string='提供商')
    name=fields.Char(string='域名')
    owner = fields.Char(string='域名所有者')
    endtime = fields.Datetime(string='到期时间')
    state = fields.Selection([('normal', '正常'), ('disabled', '已停用')],string='域名状态')
    dns = fields.Char('DNS服务器')
    contact_person = fields.Char('联系人')
    country = fields.Many2one('res.country',string='国家')
    province = fields.Many2one('res.country.state',string='省份')
    city = fields.Char(string='城市')
    address = fields.Char(string='通讯地址')
    zip = fields.Char(string='邮编')
    mail = fields.Char(string='联系人邮箱')
    phone1 = fields.Char(string='联系电话1')
    phone2 = fields.Char(string='联系电话2')
    fax=fields.Char(string='传真')
    description=fields.Text(string="描述")
    account4domain = fields.Char(string='申请账号')
    record_provider = fields.Selection([('ali', '阿里'), ('tencent', '腾讯')],string='备案系统')
    record_sys_account=fields.Char(string='备案系统账号')
    record_sys_pwd=fields.Char(string='备案系统密码')
    record_no=fields.Char(string='备案号')
    record_pwd=fields.Char(string='备案密码')
    record_description=fields.Text(string='备案描述')

    _sql_constraints = [('name_uniq', 'unique(name)', '域名必须唯一!')]

