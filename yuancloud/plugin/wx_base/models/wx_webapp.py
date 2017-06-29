# -*- coding: utf-8 -*-

import yuancloud
from yuancloud import models, fields, api, _

# 1.微信开放平台网站应用
class wx_officialaccount(models.Model):
    _name = 'wx.webapplication'
    _rec_name = "wx_webappname"

    wx_webappname = fields.Char(string="应用名称")
    wx_webappid = fields.Char(string="应用AppID")
    wx_webappsecret = fields.Char(string="应用密钥")
    wx_webapp_authwebsiteurl=fields.Char(string="授权回调域")
    wx_webapp_desc=fields.Char(string="备注")
