# -*- coding: utf-8 -*-

# from yuancloud import models, fields, api

import itertools
from lxml import etree
import urllib2
import logging

try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
from yuancloud.osv.osv import osv
import struct
import os
import time
import pytz, datetime
from collections import defaultdict
from yuancloud import http
import string
import random
from yuancloud import http
from yuancloud.api import Environment
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import user_manager as user
from yuancloud.addons.wx_base.sdks.openplatform_sdk import public_sdk
from yuancloud.addons.wx_base.sdks.openplatform_sdk import qy_open_public_sdk
from yuancloud import cache
import base64
_logger = logging.getLogger(__name__)


# class wx_customer_group(models.Model):
#     _name = 'ycloud.wx.customer_group'
#     _rec_name = 'oe_membership_id'
#     oe_membership_id = fields.Many2one('product.template', select=True,
#                                        domain="[('membership','=',True), ('type', '=', 'service')]", required=True,
#                                        string='OE会籍')
#     groupid=fields.Char(string="分组ID",readonly=True)
#     officialaccount = fields.Many2one("wx.officialaccount", required=True, string="微信服务号")
#
#     @api.one
#     def create_group(self):
#         groupname=self.oe_membership_id.name
#         print groupname
#         userManager = user.user_manager(self.officialaccount.wx_appid,self.officialaccount.wx_appsecret)
#         create_groupresult = userManager.create_user_group(groupname)
#         if 'errcode' in create_groupresult:
#             result="创建分组失败:"+str(create_groupresult['errcode'])+","+create_groupresult['errmsg']
#             raise except_osv(_('Error!'), _(result))
#         else:
#             self.groupid=create_groupresult['group']['id']
#
#     @api.one
#     def modify_group(self):
#         groupid=self.groupid
#         groupname=self.oe_membership_id.name
#         print groupid
#         print groupname
#         userManager = user.user_manager(self.officialaccount.wx_appid,self.officialaccount.wx_appsecret)
#         modify_groupresult = userManager.modify_user_group(groupid,groupname)
#         if 'errcode' in modify_groupresult:
#             if modify_groupresult['errcode']==0:
#                 pass
#             else:
#                 result="修改分组失败:"+str(modify_groupresult['errcode'])+","+modify_groupresult['errmsg']
#                 raise except_osv(_('Error!'), _(result))
#
#     @api.one
#     def delete_group(self):
#         groupid=self.groupid
#         userManager = user.user_manager(self.officialaccount.wx_appid,self.officialaccount.wx_appsecret)
#         del_groupresult = userManager.delete_user_group(groupid)
#         if 'errcode' in del_groupresult:
#             if del_groupresult['errcode']==0:
#                 pass
#             else:
#                 result="删除分组失败:"+str(del_groupresult['errcode'])+","+del_groupresult['errmsg']
#                 raise except_osv(_('Error!'), _(result))

class wx_customer(models.Model):
    _name = 'wx.customer'
    _rec_name = 'nickname'
    openid = fields.Char(string='微信ID',readonly=True)
    unionid = fields.Char(string='UNIONID',readonly=True)
    nickname = fields.Char(string='昵称',readonly=True)
    sex = fields.Selection([('male', '男'), ('female', '女'), ('other', '保密')], string='性别',readonly=True)
    country = fields.Many2one('res.country', string='国家',readonly=True)
    province = fields.Many2one('res.country.state', string='省/直辖市',readonly=True)
    city = fields.Char(string='城市',readonly=True)
    headimg = fields.Binary(string='头像',readonly=True)
    officialaccount_id = fields.Many2one('wx.officialaccount', string='服务号',readonly=True)
    # customer=fields.Many2one('')
    subscribe_infos = fields.One2many('wx.customer.subscribe','wx_customer_id',string='关注信息')

    _sql_constraints = [('openid_uniq', 'unique(openid)', '微信ID必须唯一!')]

class wx_customer_subscribe(models.Model):
    _name = 'wx.customer.subscribe'
    subscribe_type = fields.Selection([('subscribe', '关注'), ('cancel_ subscribe', '取消关注')], string='类型',readonly=True)
    subscribe_source = fields.Selection([('manual', '手工关注'), ('scan', '扫码关注')], string='来源',readonly=True)
    subscribe_time = fields.Datetime(string='操作时间',readonly=True)
    subscribe_key = fields.Char(string='Key',readonly=True)
    wx_customer_id = fields.Many2one('wx.customer',string='微信用户',readonly=True)
    #store_id =fields.Many2one('ycloud.o2o.store',string='门店',readonly=True)
    _order = 'subscribe_time desc'

#维护微信客户
class wx_customer_4subscribe:
    def __init__(self, cr, uid, context):
        self._cr = cr
        self._uid = uid
        self._context = context
    #维护微信客户（创建、修改）
    def create_wx_customer(self, values):
        try:
            env = Environment(self._cr, self._uid, self._context)
            if 'openid' in values and 'officialaccount_id' in values:
                openid=values['openid']
                officialaccount_id=values['officialaccount_id']
                #业务开始
                #1.通过openid,服务号ID调用接口，获取用户详细信息
                official_account=env['wx.officialaccount'].getofficialaccount(officialaccount_id)
                if official_account.is_auth_officialaccount:
                    if official_account.is_qyhapp:
                        # key = official_account['third_auth_SuiteId'] + "suite_access_token"
                        # suite_access_token=cache.redis.get(key)
                        # access_token=qy_open_public_sdk.get_corp_access_token(suite_access_token,official_account['third_auth_SuiteId'],official_account['wx_appid'],official_account['third_auth_code'])
                        userinfo=False
                        #userinfo=#
                        pass
                    else:
                        auth_access_token=public_sdk.get_authorizer_access_token(official_account.wx_appid,official_account.auth_component_appid,official_account.auth_component_appsecret,official_account.authorizer_refresh_token)
                        print auth_access_token
                        userinfo=user.get_user_detailinfo_access_token(openid,auth_access_token)
                        print userinfo
                else:
                    user_help = user.user_manager(official_account.wx_appid,official_account.wx_appsecret)
                    userinfo = user_help.get_user_detailinfo(openid)
                wx_customer_values={}
                wx_customer_values['openid']=values['openid']
                if userinfo:
                    # wx_customer_values['openid']=userinfo['openid']
                    wx_customer_values['nickname']=userinfo['nickname']
                    if userinfo['sex']==1:
                        wx_customer_values['sex']='male'
                    elif userinfo['sex']==2:
                        wx_customer_values['sex']='female'
                    else:
                        wx_customer_values['sex']='other'
                    headimgurl = userinfo['headimgurl']
                    if headimgurl:
                        image = urllib2.urlopen(headimgurl).read()
                        headimg=base64.b64encode(image)
                        wx_customer_values['headimg']=headimg
                    if 'province' in userinfo:
                        province = userinfo["province"]
                        sql_str = "select country_id,id as province_id from res_country_state where name  like " + "'" + province + "%'"
                        print sql_str
                        self._cr.execute(sql_str)
                        res = self._cr.fetchall()
                        if len(res) > 0:
                            country_id = res[0][0]
                            province_id = res[0][1]
                            wx_customer_values['country']=country_id
                            wx_customer_values['province']=province_id
                    wx_customer_values['city']=userinfo["city"]
                    wx_customer_values['officialaccount_id']=official_account.id
                wx_customer_instance=env['wx.customer']
                wx_customers=wx_customer_instance.search([('openid', '=', openid)])
                wx_customer_obj=0
                if len(wx_customers)==0:
                    wx_customer_obj= wx_customer_instance.create(wx_customer_values)
                else:
                    wx_customer_obj=wx_customers[0]
                    wx_customer_obj.write(wx_customer_values)
                    #

                if 'subscribe' in values:
                    wx_customer_subscribe_instance=env['wx.customer.subscribe']
                    wx_customer_subscribe_values={}
                    if values['subscribe']:
                        wx_customer_subscribe_values['subscribe_type']='subscribe'
                    else:
                        wx_customer_subscribe_values['subscribe_type']='cancel_ subscribe'
                    if 'subscribe_time' in values:
                        wx_customer_subscribe_values['subscribe_time']=values['subscribe_time']
                    else:
                        if userinfo['subscribe_time']:
                            wx_customer_subscribe_values['subscribe_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(userinfo['subscribe_time']))
                        else:
                            wx_customer_subscribe_values['subscribe_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime() )
                    if 'subscribe_source' in values:
                        wx_customer_subscribe_values['subscribe_source']=values['subscribe_source']
                    # if 'key' in values:
                    #     wx_customer_subscribe_values['subscribe_key']=values['key']
                    #     qr_management = env['ycloud.qr.management'].search(['|', ('scene_str', '=', values['key']), ('scene_id', '=', int(values['key']) if values['key'].isdigit() else -1)])
                    #     if len(qr_management)>0:
                    #         if qr_management[0].o2o_store:
                    #             wx_customer_subscribe_values['store_id']=qr_management[0].o2o_store.id

                    wx_customer_subscribe_values['wx_customer_id']=wx_customer_obj.id
                    wx_customer_subscribe_instance.create(wx_customer_subscribe_values)
                return wx_customer_obj
        except Exception as e:
            _logger.error(e)


class wx_customer_inherit(models.Model):
    _inherit = 'wx.customer'
    def search_customer(self,**kwargs):
        print kwargs
        mobile=kwargs['mobile']
        print mobile
        result=[]
        orderInfos=self.env['wx.customer'].search([])
        if orderInfos:
            for orderinfo in orderInfos:
                result.append(orderinfo)
            print result
            return result
        else:
            return []
