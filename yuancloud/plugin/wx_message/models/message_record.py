# -*- coding: utf-8 -*-
import itertools
from lxml import etree
import json
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
import logging
import time
from yuancloud import http
import xmltodict
import threading
from yuancloud import http, api, registry, models
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def _messagetype_get(obj, cr, uid, typecode, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('wx.messagetype').search(cr, uid, [('typecode', '=', typecode)], context=context)
    if ids:
        return obj.pool.get('wx.messagetype').browse(cr, uid, ids[0], context=context)
    return False

_logger = logging.getLogger(__name__)

# 微信消息类型
class wx_message_type(models.Model):
    _name = 'wx.messagetype'
    _rec_name = 'typename'
    typecode = fields.Char(string="编码")
    typename = fields.Char(string="名称")


class wx_message_record(models.AbstractModel):
    _name = 'wx.message_record'

    message_event = fields.Selection([('receive', '收'), ('send', '发')], require=True, string="消息事件类型")
    association_user=fields.Many2one('res.partner',string="关联用户")
    message_type = fields.Many2one('wx.messagetype', string='消息类型')
    officialaccount = fields.Many2one('wx.officialaccount', '微信服务号/企业号应用')
    createTime = fields.Datetime("消息创建时间")
    session_id=fields.Char("会话ID")
    message_status = fields.Selection(
        [('draft', '草稿'),('approving','审核中'),('approved','审核通过'), ('sending', '发送中'), ('use_sucess', '已接受'), ('use_block', '已拒绝'),
         ('system_fail', '发送失败')], require=True, string="消息状态",default='draft')
    usergroup=fields.Many2many('res.users','usergroup_id','user_id',string="群发企业用户")
    official_username=fields.Many2one('wx.customer',string="接收方/发送方")
    send_event=fields.Many2one('wx.message.send_event',string="消息发送事件")
    #usernamelist=fields.One2many('res.partner',string='待发送用户列表')
    #rolelist=fields.One2many('res.group',string='角色列表')

class wx_text_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.text_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'text'))
    message_content = fields.Text("消息内容")
    message_msgid = fields.Char(string="消息ID", size=128)
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    isList=fields.Boolean("是否列表")
    message_template=fields.Many2one('wx.text_message_template',string="文字消息模板")
    association_order=fields.Char('关联实体编码或单号')
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")

    @api.one
    def send_text_message(self):
        text_message_record = self
        if text_message_record['message_event']=="receive":
            raise except_osv(_('Error!'), _("请创建消息事件类型为发的消息进行发送"))
        print text_message_record['officialaccount']
        if text_message_record['message_status']<>"approved":
            raise except_osv(_('Error!'), _("未审核通过记录不允许发送"))
        if text_message_record['officialaccount']['id']==False:
            raise except_osv(_('Error!'), _("请维护对应的服务号或企业号应用信息"))
        if text_message_record['officialaccount']['is_qyhapp']==False:
            if text_message_record['toUserName']['openid']==False:
                raise except_osv(_('Error!'), _("请维护接收方信息"))
            print '服务号'
            openid=text_message_record['toUserName']['openid']
            template_code=text_message_record['message_template']['template_code']
            wxOfficeAccountInfo=text_message_record['officialaccount']
            order=text_message_record['association_order']
            model_entity_name=text_message_record['message_template']['model_id']['model']
            if order==False:
                messageinfo = reply_information.reply_information()
                print wxOfficeAccountInfo['wx_official_account_id']
                messagelist=messageinfo.text_reply_xml(openid, wxOfficeAccountInfo['wx_official_account_id'], int(time.time()), text_message_record['message_template']['message_content'])
                self.env['send_message'].sendcustommessage(messagelist)
                self.env['send_message'].insert_text_record(openid,wxOfficeAccountInfo,self.env,text_message_record['message_template']['message_content'],text_message_record['message_template'],"",False,"","sending","send")
                return
            order_jsons=json.loads(order)
            model_values=[]
            for orderinfo in order_jsons:
                value=self.env[model_entity_name].search([('id','=',orderinfo['id'])])[0]
                model_value={}
                model_value.update({
                    "id": text_message_record['message_template']['model_id']['id'],
                    "model_value": value
                })
                model_values.append(model_value)
            self.env['send_message'].send_text_message(template_code,model_values,openid,wxOfficeAccountInfo)
        else:
            print '企业号'
            userid=text_message_record['qy_toUserName']['user_id']['login']
            if userid==False:
                raise except_osv(_('Error!'), _("请维护企业应用接收方信息"))
            template_code=text_message_record['message_template']['template_code']
            wxOfficeAccountInfo=text_message_record['officialaccount']
            order=text_message_record['association_order']
            model_entity_name=text_message_record['message_template']['model_id']['model']
            if order==False:
                messageinfo = reply_information.reply_information()
                print wxOfficeAccountInfo['wx_appid']
                messagelist=messageinfo.text_reply_xml(userid, wxOfficeAccountInfo['wx_appid'], int(time.time()), text_message_record['message_template']['message_content'])
                self.env['send_message'].send_qy_custommessage(messagelist,wxOfficeAccountInfo['wx_qyh_app_id'])
                self.env['send_message'].insert_qy_text_record(userid,wxOfficeAccountInfo,self.env,text_message_record['message_template']['message_content'],text_message_record['message_template'],"",False,"","sending","send")
                return
            order_jsons=json.loads(order)
            model_values=[]
            for orderinfo in order_jsons:
                value=self.env[model_entity_name].search([('id','=',orderinfo['id'])])[0]
                model_value={}
                model_value.update({
                    "id": text_message_record['message_template']['model_id']['id'],
                    "model_value": value
                })
                model_values.append(model_value)
            self.env['send_message'].send_qy_text_message(template_code,model_values,userid,wxOfficeAccountInfo)
            pass

class wx_image_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.image_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'image'))
    message_picurl = fields.Char("图片链接地址")
    message_mediaId = fields.Char("图片消息媒体id")
    message_imagedata = fields.Binary(string="图片信息")
    message_msgid = fields.Char("消息ID")
    message_template=fields.Many2one('wx.image_message_template',string="图片消息模板")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")
    association_order=fields.Char('关联实体编码或单号')

class wx_notify_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.notify_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,'template'))
    message_msgid = fields.Char("消息ID")

    message_template=fields.Many2one('wx.notify_message_template',string="通知消息模板")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")
    message_templateid = fields.One2many('wx.notify_record_value', 'templateid', '模板记录')
    model_id = fields.Many2one('ir.model', '应用模型',help="Base model on which the server action runs.")
    association_order = fields.Char("关联实体编码或单号")

class wx_notify_message_record_value(models.Model):
    _name = 'wx.notify_record_value'
    template_key = fields.Char("模板Key")
    template_value = fields.Char("模板Value")
    template_remark = fields.Char("备注")
    templateid = fields.Many2one('wx.notify_message_record')

class wx_voice_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.voice_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'voice'))
    message_format = fields.Char("语音格式")
    message_mediaId = fields.Char("语音消息媒体id")
    message_voicedata = fields.Binary(string="语音数据")
    message_recognition = fields.Char("语音识别结果")
    message_msgid = fields.Char("消息ID")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    message_template=fields.Many2one('wx.voice_message_template',string="语音消息模板")
    association_order=fields.Char('关联实体编码或单号')

class wx_music_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.music_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'music'))
    message_title = fields.Char("音乐标题")
    message_description = fields.Char("音乐描述")
    message_musicURL = fields.Char("音乐链接")
    message_HQMusicUrl = fields.Char("高质量音乐链接")
    message_ThumbMediaId = fields.Char("缩略图的媒体id")
    message_ThumbMediaData = fields.Binary("缩略图的媒体数据")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")
    message_template=fields.Many2one('wx.music_message_template',string="音乐消息模板")
    association_order=fields.Char('关联实体编码或单号')

class wx_video_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.video_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'video'))
    message_mediaId = fields.Char("视频消息媒体id")
    message_videodata = fields.Binary(string="视频数据")
    message_thumbMediaId = fields.Char("缩略图id")
    message_thumbMediadata = fields.Binary("缩略图")
    message_msgid = fields.Char("消息ID")
    message_title = fields.Char("视频标题")
    message_description = fields.Char("视频描述")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")
    message_template=fields.Many2one('wx.video_message_template',string="视频消息模板")
    association_order=fields.Char('关联实体编码或单号')

class wx_location_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.location_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'location'))
    message_locationX = fields.Float(string="地理位置维度")
    message_locationY = fields.Float(string="地理位置经度")
    message_scale = fields.Float(string="地图缩放大小")
    message_label = fields.Char(string="地理位置信息")
    message_msgid = fields.Char("消息ID")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    message_template=fields.Many2one('wx.location_message_template',string="位置消息模板")
    association_order=fields.Char('关联实体编码或单号')
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")

class wx_link_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.link_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'link'))
    message_title = fields.Char(string="消息标题")
    message_description = fields.Char(string="消息描述")
    message_url = fields.Char(string="消息链接")
    message_msgid = fields.Char("消息ID")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")
    message_template=fields.Many2one('wx.link_message_template',string="链接消息模板")
    association_order=fields.Char('关联实体编码或单号')
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")


class wx_mpnews_message_record(models.Model):
    _inherit = 'wx.message_record'
    _name = 'wx.mpnews_message_record'
    message_type = fields.Many2one('wx.messagetype', string='消息类型',default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,'imagetext'))
    message_news = fields.One2many('wx.message_mpnews_record', 'news_id', string="图文消息")
    #toUserName = fields.Many2one('wx.membership',string="接收方/发送方")
    message_template=fields.Many2one('wx.mpnews_message_template',string="链接消息模板")
    message_title = fields.Text(string="图文消息标题")
    message_description = fields.Char(string="图文消息描述")
    message_picurl = fields.Char(string="图片链接")  # 较好的效果为大图360*200，小图200*200
    message_url = fields.Char(string="消息跳转链接")
    isList=fields.Boolean("是否列表")
    association_order=fields.Char('关联实体编码或单号')
    qy_toUserName=fields.Many2one('hr.employee',string="企业应用接收方/发送方")

class mpnew_record(models.Model):
    _name = 'wx.message_mpnews_record'
    news_id = fields.Many2one('wx.mpnews_message_record')
    message_title = fields.Text(string="图文消息标题")
    message_description = fields.Char(string="图文消息描述")
    message_picurl = fields.Char(string="图片链接")  # 较好的效果为大图360*200，小图200*200
    message_url = fields.Char(string="消息跳转链接")
    message_imagedata = fields.Binary(string="图片信息")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

















