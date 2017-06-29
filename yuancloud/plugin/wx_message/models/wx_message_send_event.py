# -*- coding: utf-8 -*-

# from yuancloud import models, fields, api

import itertools
from lxml import etree
import json
import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
import datetime
from yuancloud.http import request
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
from yuancloud.osv.osv import osv
import os
import base64
from yuancloud.api import Environment
import urllib2
from urllib import urlencode
import logging
import time
from yuancloud import http
import xmltodict
import threading
from yuancloud import http, api, registry, models
import sys
from yuancloud.addons.wx_base.sdks.enterpriseaccount_sdk import kf_manager
from yuancloud.tools.safe_eval import safe_eval as safeeval

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)


class wx_message_send_event(models.Model):
    _name = 'wx.message.send_event'
    _rec_name = "code"

    name = fields.Char("名称", required=True)
    code = fields.Char("编码", required=True)
    model_id = fields.Many2one('ir.model', '模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    command_value = fields.Char(string='命令关键字')
    command_abbreviations = fields.Char(string='命令缩写')
    command_alias = fields.Char(string='命令别名')
    command_help = fields.Char(string="命令帮助")
    method_name = fields.Char(string="扩展方法名")
    method_common=fields.Boolean(string="是否通用方法")
    version = fields.Integer(string="版本", default=1)
    iseffective = fields.Boolean(string="是否生效")
    command_params = fields.One2many('wx.command.params', 'params', '命令参数表')
    entity_trigger = fields.One2many('wx.entity.trigger', 'trigger', '实体触发时机')
    message_details = fields.One2many('wx.message.details', 'details', '消息发送明细')
    officailaccount=fields.Many2one('wx.officialaccount',string='服务应用')

    def search_customer_openids(self, userName, env, message_detail):
        str_condition = userName.replace('#客户', '')
        _logger.info("客户过滤条件:" + str_condition)
        partners = env['res.partner'].search(
            [str_condition, ('customer', '=', True), ('is_company', '=', False), ('active', '=', True)])
        _logger.info("找到客户个数:" + str(len(partners)))
        openids = []
        for partner in partners:
            wx_customers = partner.wx_customer_ids.filtered(
                lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
            for wx_customer in wx_customers:
                _logger.info("微信客户Openid:" + wx_customer['openid'])
                if wx_customer['openid'] <> False:
                    if wx_customer['openid'] not in openids:
                        openids.append(wx_customer['openid'])
        return openids

    def search_customer_group(self, groupName, env, message_detail):
        str_condition = groupName.replace('#组', '')
        _logger.info("组过滤条件:" + str_condition)
        groups = env['res.groups'].search[str_condition]
        _logger.info("找到组个数:" + str(len(groups)))
        openids = []
        for group_entity in groups:
            for user in group_entity.users:
                wx_customers = user.partner_id.wx_customer_ids.filtered(
                    lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
                for wx_customer in wx_customers:
                    _logger.info("微信客户Openid:" + wx_customer['openid'])
                    if wx_customer['openid'] <> False:
                        if wx_customer['openid'] not in openids:
                            openids.append(wx_customer['openid'])
        return openids

    def search_customer_hr(self, employeName, env, message_detail):
        str_condition = employeName.replace('#员工', '')
        _logger.info("员工过滤条件:" + str_condition)
        hr_employees = env['hr.employee'].search[str_condition, ('active', '=', True)]
        _logger.info("找到员工个数:" + str(len(hr_employees)))
        openids = []
        for hr_employee in hr_employees:
            wx_customers = hr_employee.userid.partner_id.wx_customer_ids.filtered(
                lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
            for wx_customer in wx_customers:
                _logger.info("微信客户Openid:" + wx_customer['openid'])
                if wx_customer['openid'] <> False:
                    if wx_customer['openid'] not in openids:
                        openids.append(wx_customer['openid'])
        return openids

    def get_follower_userid(self, env, follower_ids):
        openids = []
        for follower_id in follower_ids:
            users = env['res.users'].search([('partner_id', '=', follower_id.id)])
            for user in users:
                openids.append(user['login'])
        return openids

    def get_follower_openid(self, env, follower_ids, officialaccount_id):
        openids = []
        for follower_id in follower_ids:
            partner = env['res.partner'].search([('id', '=', follower_id.id)])
            if partner:
                wx_customers = partner.wx_customer_ids.filtered(
                    lambda r: r.officialaccount_id.id == officialaccount_id)
                for wx_customer in wx_customers:
                    _logger.info("微信客户Openid:" + wx_customer['openid'])
                    if wx_customer['openid'] <> False:
                        if wx_customer['openid'] not in openids:
                            openids.append(wx_customer['openid'])
        return openids

    def send_message_detail_officalaccount(self, cr, uid, message_detail, user_entity, model_instances,
                                           send_event_entity, context):
        env = Environment(cr, uid, context)
        if message_detail.username.startswith('#客户'):
            openids = self.search_customer_openids(message_detail.username, env, message_detail)
            for openid in openids:
                env['send_message'].sendMessage(cr, uid, message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, openid,
                                                message_detail.officialaccount)
        elif message_detail.username.startswith('#组'):
            openids = self.search_customer_group(message_detail.username, env, message_detail)
            for openid in openids:
                env['send_message'].sendMessage(cr, uid, message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, openid,
                                                message_detail.officialaccount)
                # todo
        elif message_detail.username.startswith("#关注者"):
            to_username = message_detail.username
            if len(model_instances) > 0:
                model_value = model_instances[0]['model_value']
                for model_instance in model_instances:
                    if model_instance['id'] == send_event_entity.model_id.id:
                        model_value = model_instance['model_value']
                        break
                follower_ids = model_value['message_follower_ids']
                openids = self.get_follower_openid(env, follower_ids, message_detail.officialaccount.id)
                for openid in openids:
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances,
                                                    openid,
                                                    message_detail.officialaccount, send_event_entity.id)
            else:
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("关注者，待发件人:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, to_username,
                                                message_detail.officialaccount, send_event_entity.id)
            pass
        elif message_detail.username.startswith('#员工'):
            openids = self.search_customer_hr(message_detail.username, env, message_detail)
            for openid in openids:
                env['send_message'].sendMessage(cr, uid, message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, openid,
                                                message_detail.officialaccount)
        else:
            to_username = message_detail.username
            if message_detail.usertype == "wx_customer":
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("待发件微信客户:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, to_username,
                                                message_detail.officialaccount, send_event_entity.id)
            elif message_detail.usertype == "wx_membership":
                if len(model_instances) > 0:
                    to_username = env['send_message'].replacecontent(to_username, model_instances[0], user_entity,
                                                                     context)
                    print to_username
                    pass
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("WX会员，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            elif message_detail.usertype == "oe_customer":  # OE客户
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        print userlist
                        for userid in userlist:
                            user_info_entity = env['res.partner'].search([('id', '=', userid)])
                            wx_customers = user_info_entity.wx_customer_ids.filtered(
                                lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
                            for wx_customer in wx_customers:
                                _logger.info("OE客户,微信客户信息：" + wx_customer['openid'] + "," + str(wx_customer['id']))
                                env['send_message'].sendMessage(message_detail.message_template_code,
                                                                message_detail.message_template_type, model_instances,
                                                                wx_customer['openid'],
                                                                message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE客户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            elif message_detail.usertype == "oe_user":  # OE用户
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        print userlist
                        for userid in userlist:
                            user_info_entity = env['res.users'].search([('id', '=', userid)])
                            wx_customers = user_info_entity.partner_id.wx_customer_ids.filtered(
                                lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
                            for wx_customer in wx_customers:
                                _logger.info("OE用户,微信客户信息：" + wx_customer['openid'] + "," + str(wx_customer['id']))
                                env['send_message'].sendMessage(message_detail.message_template_code,
                                                                message_detail.message_template_type, model_instances,
                                                                wx_customer['openid'],
                                                                message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE用户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            elif message_detail.usertype == "oe_employee":  # OE员工
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        print userlist
                        for userid in userlist:
                            str_condition = "('id','='," + userid + ")"
                            print str_condition
                            openids = self.search_customer_hr(str_condition, env, message_detail)
                            # user_info_entity=env['hr.employee'].search([('id','=',userid)])
                            # wx_customers = user_info_entity.partner_id.wx_customer_ids.filtered(lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
                            for openid in openids:
                                _logger.info("OE员工:" + openid)
                                env['send_message'].sendMessage(message_detail.message_template_code,
                                                                message_detail.message_template_type, model_instances,
                                                                openid,
                                                                message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE用户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
                pass
            elif message_detail.usertype == "store.user":  # 门店员工
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        print userlist
                        for userid in userlist:
                            user_info_entity = env['ycloud.o2o.storeusers'].search([('id', '=', userid)])
                            wx_customers = user_info_entity.user_id.partner_id.wx_customer_ids.filtered(
                                lambda r: r.officialaccount_id.id == message_detail.officialaccount.id)
                            for wx_customer in wx_customers:
                                _logger.info("门店员工,微信客户信息：" + wx_customer['openid'] + "," + str(wx_customer['id']))
                                env['send_message'].sendMessage(message_detail.message_template_code,
                                                                message_detail.message_template_type, model_instances,
                                                                wx_customer['openid'],
                                                                message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("门店员工，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
            else:
                print context
                print to_username
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("服务号，待发件人:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)

    def send_message_detail_qy(self, cr, uid, message_detail, user_entity, model_instances,
                               send_event_entity, context):
        env = Environment(cr, uid, context)
        if message_detail.username.startswith('#客户'):
            str_condition = message_detail.username.replace('#客户', '')
            _logger.info("客户过滤条件:" + str_condition)
            partners = env['res.partner'].search(
                [str_condition, ('customer', '=', True), ('is_company', '=', False)])
            _logger.info("找到客户个数:" + str(len(partners)))
            userlist = ""
            for partner in partners:
                users = env['res.users'].search([('partner_id', '=', partner.id), ('active', '=', True)])
                for user in users:
                    _logger.info("用户LoginID:" + user['login'])
                    if user['login']:
                        if user['login'] not in userlist:
                            userlist = userlist + user['login'] + "|"
            if userlist.endswith('|'):
                userlist = userlist[:-1]
            if userlist <> "":
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, userlist,
                                                message_detail.officialaccount, send_event_entity.id)
        elif message_detail.username.startswith('#组'):
            str_condition = message_detail.username.replace('#组', '')
            _logger.info("组过滤条件:" + str_condition)
            groups = env['res.groups'].search[str_condition]
            _logger.info("找到组个数:" + str(len(groups)))
            userlist = ""
            for group_entity in groups:
                for user in group_entity.users:
                    _logger.info("用户LoginID:" + user['login'])
                    if user['login']:
                        if user['login'] not in userlist:
                            userlist = userlist + (user['login']) + "|"
            if userlist.endswith('|'):
                userlist = userlist[:-1]
            if userlist <> "":
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, userlist,
                                                message_detail.officialaccount, send_event_entity.id)
            # todo
            pass
        elif message_detail.username.startswith('#员工'):
            str_condition = message_detail.username.replace('#员工', '')
            _logger.info("员工过滤条件:" + str_condition)
            hr_employees = env['hr.employee'].search[str_condition, ('active', '=', True)]
            _logger.info("找到员工个数:" + str(len(hr_employees)))
            userlist = ""
            for hr_employee in hr_employees:
                user = hr_employee.userid
                _logger.info("用户LoginID:" + user['login'])
                if user['login']:
                    if user['login'] not in userlist:
                        userlist = userlist + user['login'] + "|"
                if userlist.endswith('|'):
                    userlist = userlist[:-1]
                if userlist <> "":
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, userlist,
                                                    message_detail.officialaccount, send_event_entity.id)
                    # todo
        elif message_detail.username.startswith('#关注者'):
            to_username = message_detail.username
            if len(model_instances) > 0:
                model_value = model_instances[0]['model_value']
                for model_instance in model_instances:
                    if model_instance['id'] == send_event_entity.model_id.id:
                        model_value = model_instance['model_value']
                        break
                userlist = ""
                userids = self.get_follower_userid(env,model_value['message_follower_ids'])
                for userid in userids:
                    userlist = userid + "|"
                if userlist.endswith('|'):
                    userlist = userlist[:-1]
                if userlist <> "":
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, userlist,
                                                    message_detail.officialaccount, send_event_entity.id)
            else:
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("OE客户，待发件人:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, to_username,
                                                message_detail.officialaccount, send_event_entity.id)
        else:
            to_username = message_detail.username
            if message_detail.usertype == "wx_customer":
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("待发件微信企业用户:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, to_username,
                                                message_detail.officialaccount, send_event_entity.id)
            elif message_detail.usertype == "wx_membership":
                # todo
                pass
                # if len(model_instances)>0:
                #     to_username = env['send_message'].replacecontent(to_username,model_instances[0], user_entity, context)
                #     print to_username
                #     pass
                # else:
                #     to_username = env['send_message'].replacecontent(to_username,{}, user_entity, context)
                #     _logger.info("WX会员，待发件人:" + to_username)
                #     env['send_message'].sendMessage(message_detail.message_template_code,
                #                                 message_detail.message_template_type, model_instances, to_username,
                #                                 message_detail.officialaccount, send_event_entity.id)
                # pass
            elif message_detail.usertype == "oe_customer":  # OE客户
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        useridlist = ""
                        print userlist
                        for userid in userlist:
                            user_info_entity = env['res.partner'].search([('id', '=', userid)])
                            users = user_info_entity.user_ids
                            for user in users:
                                _logger.info("用户LoginID:" + user['login'])
                                if user['login']:
                                    if user['login'] not in useridlist:
                                        useridlist = useridlist + user['login'] + "|"
                        if useridlist.endswith('|'):
                            useridlist = useridlist[:-1]
                        if useridlist <> "":
                            env['send_message'].sendMessage(message_detail.message_template_code,
                                                            message_detail.message_template_type, model_instances,
                                                            useridlist,
                                                            message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE客户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            elif message_detail.usertype == "oe_user":  # OE用户
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    print to_username
                    try:
                        userlist = eval(to_username)
                        useridlist = ""
                        print userlist
                        for userid in userlist:
                            user = env['res.users'].search([('id', '=', userid)])
                            _logger.info("用户LoginID:" + user['login'])
                            if user['login']:
                                if user['login'] not in useridlist:
                                    useridlist = useridlist + user['login'] + "|"
                        if useridlist.endswith('|'):
                            useridlist = useridlist[:-1]
                        if useridlist <> "":
                            env['send_message'].sendMessage(message_detail.message_template_code,
                                                            message_detail.message_template_type, model_instances,
                                                            useridlist,
                                                            message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE用户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            elif message_detail.usertype == "oe_employee":  # OE员工
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        print userlist
                        useridlist = ""
                        for userid in userlist:
                            hr_employees = env['hr.employee'].search[('id', '=', userid), ('active', '=', True)]
                            _logger.info("找到员工个数:" + str(len(hr_employees)))
                            userlist = ""
                            for hr_employee in hr_employees:
                                user = hr_employee.userid
                                _logger.info("用户LoginID:" + user['login'])
                                if user['login']:
                                    if user['login'] not in useridlist:
                                        useridlist = useridlist + user['login'] + "|"
                        if useridlist.endswith('|'):
                            useridlist = useridlist[:-1]
                        if useridlist <> "":
                            env['send_message'].sendMessage(message_detail.message_template_code,
                                                            message_detail.message_template_type, model_instances,
                                                            useridlist,
                                                            message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("OE用户，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
                pass
            elif message_detail.usertype == "store.user":  # 门店员工
                if len(model_instances) > 0:
                    model_value = model_instances[0]['model_value']
                    for model_instance in model_instances:
                        if model_instance['id'] == send_event_entity.model_id.id:
                            model_value = model_instance['model_value']
                            break
                    to_username = env['send_message'].replacecontent(to_username, model_value, user_entity, context)
                    try:
                        userlist = eval(to_username)
                        useridlist = ""
                        print userlist
                        for userid in userlist:
                            user_info_entity = env['ycloud.o2o.storeusers'].search([('id', '=', userid)])
                            user = user_info_entity.user_id
                            if user['login']:
                                if user['login'] not in useridlist:
                                    useridlist = useridlist + user['login'] + "|"
                        if useridlist.endswith('|'):
                            useridlist = useridlist[:-1]
                        if useridlist <> "":
                            env['send_message'].sendMessage(message_detail.message_template_code,
                                                            message_detail.message_template_type, model_instances,
                                                            useridlist,
                                                            message_detail.officialaccount, send_event_entity.id)
                    except:
                        env['send_message'].sendMessage(message_detail.message_template_code,
                                                        message_detail.message_template_type, model_instances,
                                                        to_username,
                                                        message_detail.officialaccount, send_event_entity.id)
                else:
                    to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                    _logger.info("门店员工，待发件人:" + to_username)
                    env['send_message'].sendMessage(message_detail.message_template_code,
                                                    message_detail.message_template_type, model_instances, to_username,
                                                    message_detail.officialaccount, send_event_entity.id)
                pass
            else:
                to_username = env['send_message'].replacecontent(to_username, {}, user_entity, context)
                _logger.info("待发件人信息:" + to_username)
                env['send_message'].sendMessage(message_detail.message_template_code,
                                                message_detail.message_template_type, model_instances, to_username,
                                                message_detail.officialaccount, send_event_entity.id)

    def send_message_detail(self, cr, uid, message_detail, user_entity, model_instances,
                            send_event_entity, context):
        # env = Environment(cr, uid, context)
        if message_detail.officialaccount == False:
            # todo
            return
        if message_detail.officialaccount.is_qyhapp == False:
            _logger.info("服务号")
            self.send_message_detail_officalaccount(cr, uid, message_detail, user_entity, model_instances,
                                                    send_event_entity, context)
        else:
            _logger.info("企业号")
            self.send_message_detail_qy(cr, uid, message_detail, user_entity, model_instances, send_event_entity,
                                        context)
    def sendmessage_event_entitys(self,cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context):
        for send_event_entity in send_event_entitys:
            if send_event_entity.officailaccount.id<>False and send_event_entity.officailaccount.id<>wxOfficeAccountInfo.id:
                _logger.info("服务号不一致，无须发送信息")
                continue
            if send_event_entity.method_name == False or send_event_entity.method_name == "":
                _logger.info("未维护扩展方法名，无需调用命令参数表")
                _logger.info("发送明细长度:" + str(len(send_event_entity.message_details)))
                for message_detail in send_event_entity.message_details:
                    try:
                        self.send_message_detail(cr, uid, message_detail, user_entity, model_instances,
                                                 send_event_entity, context)
                    except:
                        _logger.error("发送信息出错:")
            else:
                _logger.info("找到扩展方法名" + send_event_entity.method_name)
                contents = commands
                print contents
                if send_event_entity.command_params:
                    _logger.info("维护方法参数")
                    if send_event_entity.method_common:
                        pass
                        condition=""
                        models={}
                        i=0
                        for content in contents:
                            param="param"+str(i)
                            models.update({
                                param:content
                            })
                            i=i+1
                        print models
                        search_cond=env['send_message'].replacecontent(send_event_entity.command_params[0]['parameter_name'], models, user_entity, context)
                        print search_cond
                        search_cond=safeeval(search_cond)
                        offset=0
                        try:
                            for param in send_event_entity.command_params:
                                if param['parameter_code']=='offset':
                                    offset=(int)(env['send_message'].replacecontent(param['parameter_name'], models, user_entity, context))
                        except Exception:
                            offset=0
                        for message_detail in send_event_entity.message_details:
                            if message_detail.message_template_type.typecode == "list":
                                _logger.info("列表消息,默认取５条记录")
                                limit = 5
                            else:
                                limit = 1
                            try:
                                for param in send_event_entity.command_params:
                                    if param['parameter_code']=='limit':
                                        limit=(int)(env['send_message'].replacecontent(param['parameter_name'], models, user_entity, context))
                            except:
                                pass
                        # k=0
                        # for param in send_event_entity.command_params:
                        #     if k==0:
                        #         conditon_value=env['send_message'].replacecontent(param['parameter_name'], models, user_entity, context)
                        #         #condition="'"+param['parameter_code']+"',='"+conditon_value+"'"
                        #         condition=(param['parameter_code'],param['parameter_operator'],conditon_value)
                        #         k=k+1
                        #     else:
                        #         conditon_value=env['send_message'].replacecontent(param['parameter_name'], models, user_entity, context)
                        #         condition=condition,(param['parameter_code'],param['parameter_operator'],conditon_value)
                        # print condition
                        # search_cond=[]
                        # if len(send_event_entity.command_params)>1:
                        #     for cond in condition:
                        #         search_cond.append(cond)
                        #     print search_cond
                        # else:
                        #     search_cond.append(condition)
                        # print search_cond
                            print limit
                            _logger.info("limit:"+str(limit))
                            model_values=env[send_event_entity.model_id.model].search(search_cond,limit=limit,offset=offset)
                            model_instances = []
                            for model_value in model_values:
                                model_instance = {}
                                model_instance.update({
                                    "id": send_event_entity['model_id']['id'],
                                    "model_value": model_value
                                })
                                model_instances.append(model_instance)
                            if len(model_instances)==0:
                                model_instance = {}
                                model_instance.update({
                                    "id":"",
                                    "model_value": ""
                                })
                                model_instances.append(model_instance)
                                command="nofound"
                                send_event_entitys = env['wx.message.send_event'].search(
                                    ['|', '|', ('command_value', '=', command), ('command_abbreviations', '=', command),
                                    ('command_alias', '=', command), ('iseffective', '=', True)], order='version desc')
                                if send_event_entitys:
                                    self.sendmessage_event_entitys(cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context)
                            else:
                                try:
                                    self.send_message_detail(cr, uid, message_detail, user_entity,
                                                             model_instances, send_event_entity, context)
                                except:
                                    _logger.error("发送信息出错:")
                    else:
                        kwarg = {}
                        for param in send_event_entity.command_params:
                            if param['parameter_sequence'] >= len(contents):
                                kwarg.update({
                                    param['parameter_code']: env['send_message'].replacecontent(param['parameter_name'], {}, user_entity, context)
                                })
                            else:
                                if param['parameter_sequence']<0:
                                    kwarg.update({
                                        param['parameter_code']: env['send_message'].replacecontent(param['parameter_name'], {}, user_entity, context)
                                    })
                                else:
                                    kwarg.update({
                                        param['parameter_code']: env['send_message'].replacecontent(contents[param['parameter_sequence']], {}, user_entity, context)
                                    })
                        model_values = getattr(env[send_event_entity.model_id.model], send_event_entity.method_name)(
                            **kwarg)
                        model_instances = []
                        if len(model_values)==0:
                            model_instance = {}
                            model_instance.update({
                                "id":"",
                                "model_value": ""
                            })
                            model_instances.append(model_instance)
                            command="nofound"
                            send_event_entitys = env['wx.message.send_event'].search(
                                ['|', '|', ('command_value', '=', command), ('command_abbreviations', '=', command),
                                ('command_alias', '=', command), ('iseffective', '=', True)], order='version desc')
                            if send_event_entitys:
                                self.sendmessage_event_entitys(cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context)
                        else:
                            for model_value in model_values:
                                model_instance = {}
                                model_instance.update({
                                    "id": send_event_entity['model_id']['id'],
                                    "model_value": model_value
                                })
                                model_instances.append(model_instance)
                            for message_detail in send_event_entity.message_details:
                                try:
                                    self.send_message_detail(cr, uid, message_detail, user_entity,
                                                             model_instances, send_event_entity, context)
                                except:
                                    _logger.error("发送信息出错:")
                else:
                    _logger.info("未维护方法参数，直接调用模型通用查询方法")
                    offset=0
                    if len(contents)>1:
                        try:
                            offset=(int)(contents[1])
                        except:
                            offset=0
                    for message_detail in send_event_entity.message_details:
                        limit = 1
                        model_instances = []
                        model_info = send_event_entity.model_id.model
                        if message_detail.message_template_type.typecode == "list":
                            _logger.info("列表消息,默认取５条记录")
                            limit = 5
                        else:
                            limit = 1
                        model_values = env[model_info].search([], limit=limit,offset=offset)
                        if len(model_values)==0:
                            model_instance = {}
                            model_instance.update({
                                "id":"",
                                "model_value": ""
                            })
                            model_instances.append(model_instance)
                            command="nofound"
                            send_event_entitys = env['wx.message.send_event'].search(
                                ['|', '|', ('command_value', '=', command), ('command_abbreviations', '=', command),
                                ('command_alias', '=', command), ('iseffective', '=', True)], order='version desc')
                            if send_event_entitys:
                                self.sendmessage_event_entitys(cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context)
                        else:
                            for model_value in model_values:
                                print model_value
                                model_instance = {}
                                model_instance.update({
                                    "id": send_event_entity['model_id']['id'],
                                    "model_value": model_value
                                })
                                model_instances.append(model_instance)
                            try:
                                self.send_message_detail(cr, uid, message_detail, user_entity,
                                                         model_instances, send_event_entity, context)
                            except:
                                _logger.error("发送信息出错:")
                

    def sendmessage_TriggeredbyCommand(self, cr, uid, command_value, model_instances,wxOfficeAccountInfo, context):
        context=context.copy()
        isqy_app=wxOfficeAccountInfo.is_qyhapp
        context.update({
            "currentTime":datetime.datetime.now()
        })
        env = Environment(cr, uid, context)
        commands = command_value.split(' ')
        command = commands[0]
        user_entity = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        # qr_management = env['ycloud.qr.management'].search(
        #     ['|', ('scene_str', '=', command), ('scene_id', '=', int(command) if command.isdigit() else -1)])
        send_event_entitys = env['wx.message.send_event'].search(
            ['|', '|', ('command_value', '=', command), ('command_abbreviations', '=', command),
             ('command_alias', '=', command), ('iseffective', '=', True)], order='version desc')
        if send_event_entitys:
            self.sendmessage_event_entitys(cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context)
        else:
            _logger.error("无法找到关键字:" + command + "对应的消息发送事件")
            _logger.info("走默认关键字default_key对应的数据")
            command="default_key"
            send_event_entitys = env['wx.message.send_event'].search(
            ['|', '|', ('command_value', '=', command), ('command_abbreviations', '=', command),
             ('command_alias', '=', command), ('iseffective', '=', True)], order='version desc')
            if send_event_entitys:
                self.sendmessage_event_entitys(cr,uid,send_event_entitys,user_entity,wxOfficeAccountInfo,commands,model_instances,env,context)
            sendtype='openid'
            # if isqy_app:
            #     sendtype='userid'
            # corpid='wxe28ca91a338a7638'
            # corpsercret="yVT4Fh_y1jHPMnF6xON-VJtD5Z3CwDHTulet9DdVHM-ZdFnRWpdJodUUVm26_xej"
            # kfmanager=kf_manager.kf_manager(corpid,corpsercret)
            # to_username="${ctx.openid}"
            # sender_value = env['send_message'].replacecontent(to_username, {}, user_entity, context)
            # kfmanager.sendtextmessage(sendtype,sender_value,"kf",'yinx',command_value)

class wx_command_params(models.Model):
    _name = 'wx.command.params'
    parameter_sequence = fields.Integer("参数序号", default=1)
    parameter_name = fields.Char("参数默认值")
    parameter_code = fields.Char("参数编码")
    parameter_desc = fields.Char("参数描述")
    parameter_operator = fields.Selection(
        [('=', '='), ('!=', '!='), ('>=', '>='), ('>', '>'), ('<', '<'), ('<=', '<='), ('=?', '=?'),
         ('=like', '=like'),('like', 'like'),('not like', 'not like'),('ilike', 'ilike'),('not ilike', 'not ilike'),('=ilike', '=ilike'),('in', 'in'),('not in', 'not in'),('child_of', 'child_of')], string="操作符")
    params = fields.Many2one("wx.message_send_event")

class wx_entity_trigger(models.Model):
    _name = 'wx.entity.trigger'
    column_code = fields.Many2one('ir.model.fields', string="属性实体")
    column_name = fields.Char("属性名称")
    column_type = fields.Char("属性类型")
    operator = fields.Selection(
        [('=', '='), ('!=', '!='), ('>=', '>='), ('>', '>'), ('<', '<'), ('<=', '<='), ('IsNull', 'IsNull'),
         ('IsNotNull', 'IsNotNull')], string="操作符")
    column_value = fields.Char(string="属性值")
    trigger = fields.Many2one("wx.message_send_event")

class wx_message_params(models.Model):
    _name = 'wx.message.details'
    username = fields.Char(string="收件人")
    message_template_type = fields.Many2one('wx.messagetype', string='消息模板类型')
    message_template_code = fields.Char(string="消息模板编码")
    officialaccount = fields.Many2one('wx.officialaccount', '微信服务号')
    usertype = fields.Selection(
        [('wx_customer', '微信客户'), ('wx_membership', '微信会员'), ('oe_customer', 'OE客户'), ('oe_user', 'OE用户'),
         ('oe_employee', 'OE员工'), ('store.user', '门店员工')], string="收件人类型")
    details = fields.Many2one('wx.message_send_event')

class wx_tools(models.AbstractModel):
    _name = "wx_tools"

    def search_music(self,**kwargs):
        print kwargs
        title=kwargs.get('title','')
        author=kwargs.get('author','')

        if title=="":
            return []
        try:
            if author=="" or author==False:
                url="http://box.zhangmen.baidu.com/x?op=12&count=1&title="+title+"$$$$$$"
            else:
                url="http://box.zhangmen.baidu.com/x?op=12&count=1&title="+title+"$$"+author+"$$$$"
            response = urllib2.urlopen(url)
            html = response.read().decode("utf-8")
            _logger.info("url:"+url)
            encode =  re.compile('<encode>.*?CDATA\[(.*?)\]].*?</encode>',re.S).findall(html)[0]
            decode =  re.compile('<decode>.*?CDATA\[(.*?)\]].*?</decode>',re.S).findall(html)[0]
            print encode
            print decode
            musiclink = encode[:encode.rindex('/')+1] + decode
            music=[]
            musicinfo={}
            musicinfo.update({
                "title":title,
                "desc":author or '未知',
                "musiclink":musiclink
            })
            music.append(musicinfo)
            return music
        except Exception as e:
            _logger.error("搜索音乐出错:"+str(e))
            return []

    def search_weather(self,**kwargs):
        print kwargs
        city=kwargs.get('city','')
        if city==False or city=="":
            return []
        currenttime=int(time.time())
        try:
            url="http://apix.sinaapp.com/weather/?appkey="+str(currenttime)+"&city="+(city)
            response = urllib2.urlopen(url)
            html = response.read().decode("utf-8")
            tokeninfo = json.loads(html)
            print tokeninfo
            weather=[]
            for token in tokeninfo:
                weatherinfo={}
                weatherinfo.update({
                    "title":token['Title'],
                    "description":token['Description'],
                    "picUrl":token['PicUrl'],
                    "url":token['Url'],
                    "city":city
                })
                weather.append(weatherinfo)
            return weather
        except Exception as e:
            _logger.error("搜索天气出错:"+str(e))
            return []






