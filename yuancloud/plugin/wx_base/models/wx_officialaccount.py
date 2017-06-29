# -*- coding: utf-8 -*-
import yuancloud
from yuancloud import models, fields, api, _
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
import json


#服务号实体
class wx_officialaccount(models.Model):
    _name = 'wx.officialaccount'
    _rec_name = 'wx_name'
    wx_appid = fields.Char(string="应用ID")
    wx_appsecret = fields.Char(string="应用密钥")
    wx_name = fields.Char(string="名称")
    wx_company = fields.Many2one("res.company", string='公司')
    wx_mch_id = fields.Char(string="商户号")
    wx_mch_secret = fields.Char(string="商户密钥")
    wx_desc=fields.Char(string="备注")
    name = yuancloud.fields.Char(related='wx_name')

class wx_qyh(models.Model):
    _name = 'wx.qyh'
    _rec_name = 'wx_qyh_name'
    wx_qyh_id = fields.Char(string="企业号ID")
    wx_qyh_name = fields.Char(string="企业号名称")
    wx_qyh_mch_id = fields.Char(string="商户号")
    wx_company = fields.Many2one("res.company", string='公司')
    wx_qyh_desc=fields.Char(string="备注")

class wx_qyh_app(models.Model):
    _inherit = 'wx.officialaccount'
    is_qyhapp = fields.Boolean(string='是否企业号应用', default=False)
    wx_qyh_app_id=fields.Integer(string="企业应用序号")
    wx_qyh = fields.Many2one('wx.qyh', string="企业号")
