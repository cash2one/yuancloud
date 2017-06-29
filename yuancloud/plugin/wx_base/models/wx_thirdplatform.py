# -*- coding: utf-8 -*-

from yuancloud import models, fields, api, _

class ycloud_wx_thirdplatform(models.Model):
    _name = 'wx.third_platform'
    _rec_name = 'auth_component_platformname'
    auth_component_appid=fields.Char("第三方平台Appid")
    auth_component_appsecret=fields.Char("第三方平台Appsecret")
    auth_component_token=fields.Char("第三方平台Token")
    auth_component_encodingasekey=fields.Char("第三方平台消息加解密密钥")
    auth_component_platformname=fields.Char("第三方平台名称")
    auth_component_platfromtype=fields.Selection([('openplatform', '公众号开放平台'), ('thirdpart', '企业号第三方应用'), ('session_service', '企业号会话服务'), ('customer_service', '企业号客服服务')],string="第三方平台类型")

