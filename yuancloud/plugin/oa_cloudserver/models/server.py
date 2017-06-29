# -*- coding: utf-8 -*-
# from openerp import models, fields, api
import logging

try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields

_logger = logging.getLogger(__name__)


class cloudserver_server(models.Model):
    '''
    实体：
    '''
    _name = 'oa.cloudserver.server'
    provider = fields.Selection([('ali', '阿里'), ('tencent', '腾讯')],string='提供商')
    uses = fields.Selection([('app', '应用'), ('db', '数据库'),('app+db','应用＋数据库'),('mail','邮箱')],string='用途')
    server_id = fields.Char(string='服务器ID')
    server_name = fields.Char(string='服务器名称')
    local = fields.Char(string='地域')
    area = fields.Char(string='所在可用区')
    use_desp = fields.Char('用途简述')
    description = fields.Text('描述')
    cpu = fields.Char(string='CPU')
    memory = fields.Char(string='内存(G)')
    disk = fields.Char(string='硬盘(G)')
    os = fields.Selection([('windows', 'Windows Server'), ('ubuntu', 'Ubuntu')],string='操作系统')
    ip_internet = fields.Char(string='公网IP')
    ip_intranet = fields.Char(string='内网IP')
    # bill_method = fields.Char(string='带宽计费方式')
    bandwidth = fields.Char(string='带宽(M)')
    # pay_method = fields.Selection([('pack_year_month', '包年包月'), ('flow_rate', '按流量')],string='付费方式')
    createon = fields.Datetime(string='创建时间')
    endon = fields.Datetime(string='到期时间')
    domain_name = fields.Char(string='域名')
    account4app = fields.Char(string='申请账号')
    login_name = fields.Char(string='用户名')
    login_pwd=fields.Char(string='密码')
    data_disk = fields.Char(string='数据盘(G)')
    _sql_constraints = [('server_id_uniq', 'unique(server_id)', '服务器ID必须唯一!')]



