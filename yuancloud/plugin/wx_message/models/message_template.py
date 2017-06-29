# -*- coding: utf-8 -*-

# from yuancloud import models, fields, api

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

class wx_message_template(models.AbstractModel):
    _name = 'wx.message_template_base'
    _rec_name = "template_code"

    template_name = fields.Char("模板名称",required=True)
    template_code = fields.Char("模板编码",required=True)
    message_type = fields.Many2one('wx.messagetype', string='消息类型')
    #officialaccount = fields.Many2one('wx.officialaccount', string='微信服务号')
    iseffective = fields.Boolean('是否生效')

class wx_text_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.text_message_template'

    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'text'))
    message_content = fields.Text("文字消息内容")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_location_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.location_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'location'))
    message_locationX = fields.Float(string="地理位置维度")
    message_locationY = fields.Float(string="地理位置经度")
    message_scale = fields.Float(string="地图缩放大小")
    message_label = fields.Char(string="地理位置信息")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_notify_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.notify_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'template'))
    message_wxtemplate_id = fields.Many2one('wx.notify_templates', '微信模板')

class templates(models.Model):
    _name = "wx.notify_templates"
    _rec_name = 'templates_remark'
    message_wx_templateid = fields.Char('微信模板ID')
    message_template_url=fields.Char("跳转地址")
    officialaccount = fields.Many2one("wx.officialaccount", '微信服务号')
    templates_remark = fields.Char("模板使用说明")
    message_templateid = fields.One2many('wx.notify_templates_value', 'templateid', '模板KEYS')
    model_id = fields.Many2one('ir.model', '应用模型',  help="Base model on which the server action runs.")

class templates_value(models.Model):
    _name = "wx.notify_templates_value"
    template_key = fields.Char("模板Key")
    template_value = fields.Char("模板Value")
    template_remark = fields.Char("备注")
    templateid = fields.Many2one('wx.notify_templates')

class wx_voice_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.voice_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'voice'))
    message_voicedata = fields.Binary(string="语音数据")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_music_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.music_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'music'))
    message_title = fields.Char("音乐标题")
    message_description = fields.Char("音乐描述")
    message_musicURL = fields.Char("音乐链接")
    message_HQMusicUrl = fields.Char("高质量音乐链接")
    message_ThumbMediaData = fields.Binary("缩略图的媒体数据")
    message_ThumbMediaId=fields.Char("缩略图的媒体id")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_video_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.video_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'video'))
    message_videodata = fields.Binary(string="视频数据")
    message_videodata_url=fields.Char(string="视频数据地址",readonly=True)
    message_thumbMediadata = fields.Binary("缩略图")
    message_thumbMedia_url=fields.Char("缩略图地址",readonly=True)
    message_title = fields.Char("视频标题")
    message_description = fields.Char("视频描述")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_image_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.image_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id, 'image'))
    message_imagedata = fields.Binary(string="图片信息")
    message_url=fields.Char(string="图片链接地址")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_link_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.link_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型', readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'link'))
    message_title = fields.Char(string="链接消息标题")
    message_description = fields.Char(string="链接消息描述")
    message_url = fields.Char(string="链接消息地址")
    model_id = fields.Many2one('ir.model', '应用模型', ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class wx_mpnews_message_template(models.Model):
    _inherit = 'wx.message_template_base'
    _name = 'wx.mpnews_message_template'
    message_type = fields.Many2one('wx.messagetype', string='消息类型',
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'imagetext'))
    message_news = fields.One2many('wx.message_mpnews_template', 'news_id', string="图文消息")
    message_title = fields.Text(string="图文消息标题")
    message_description = fields.Char(string="图文消息描述")
    message_picurl = fields.Char(string="图片链接")  # 较好的效果为大图360*200，小图200*200
    message_url = fields.Char(string="消息跳转链接")
    message_imagedata = fields.Binary(string="图片信息")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class news(models.Model):
    _name = 'wx.message_mpnews_template'
    news_id = fields.Many2one('wx.mpnews_message_template')
    message_title = fields.Text(string="图文消息标题")
    message_description = fields.Char(string="图文消息描述")
    message_picurl = fields.Char(string="图片链接")  # 较好的效果为大图360*200，小图200*200
    message_url = fields.Char(string="消息跳转链接")
    message_imagedata = fields.Binary(string="图片信息")
    model_id = fields.Many2one('ir.model', '应用模型',  ondelete='cascade', copy=False,
                               help="Base model on which the server action runs.")

class list_message_template(models.Model):
    _name = "list.message_template"
    _inherit = 'wx.message_template_base'
    message_type = fields.Many2one('wx.messagetype', string='消息类型',readonly=True,
                                   default=lambda self: _messagetype_get(self, self.env.cr, self.env.user.id,
                                                                         'list'))
    message_template_type=fields.Many2one('wx.messagetype',required=True,string='消息模板类型',domain=[('typecode','in',('text','imagetext'))])
    message_template_code=fields.Char(string="消息模板编码",required=True)


