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
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import media_manager
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
import base64
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import custom_manager
import xmltodict
import send_message
import threading
from yuancloud import http, api, registry, models

_logger = logging.getLogger(__name__)


class receive_message(models.AbstractModel):
    def accept_qy_message(self, cr, uid, messageType, vals, agentid, context):
        try:
            if messageType == "wx.image_message_record":
                return self.create_qy_image_record(cr, uid, vals, agentid, context)
            elif messageType == "wx.voice_message_record":
                return self.create_qy_voice_record(cr, uid, vals, agentid, context)
            elif messageType == "wx.link_message_record":
                return self.create_qy_link_record(cr, uid, vals, agentid, context)
            elif messageType == "wx.location_message_record":
                return self.create_qy_location_record(cr, uid, vals, agentid, context)
            elif messageType == "wx.video_message_record":
                return self.create_qy_video_record(cr, uid, vals, agentid, context)
            elif messageType == "wx.message_text":
                return self.create_qy_text_record(cr, uid, vals, agentid, context)
            pass
        except Exception as e:
            _logger.info("接受企业号消息出错:" + str(e))

    def create_qy_image_record(self,cr, uid, vals, agentid, context):
        pass

    def create_qy_voice_record(self,cr, uid, vals, agentid, context):
        pass

    def create_qy_link_record(self,cr, uid, vals, agentid, context):
        pass

    def create_qy_location_record(self,cr, uid, vals, agentid, context):
        pass

    def create_qy_video_record(self,cr, uid, vals, agentid, context):
        pass

    def create_qy_text_record(self,cr, uid, jsonStr, agentid, context):
        content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        MsgId = jsonStr['MsgId']
        env = Environment(cr, uid, context)
        wxOfficeAccountInfo = env['wx.officialaccount'].search(
            [('wx_appid', '=', toUser), ('wx_qyh_app_id', '=', agentid)])[0]
        text_template = {}
        text_template.update({
            "id": ""
        })
        try:
            env['send_message'].insert_qy_text_record(fromUser, wxOfficeAccountInfo, env, content, text_template, "",
                                                   False, MsgId, 'use_sucess', 'receive')
        except Exception as e:
            _logger.info("插入企业号文本消息记录出错:" + str(e))
        cr.commit()
        threaded_run = threading.Thread(target=self.processmessage,
                                        args=(fromUser, cr, uid, context, content, wxOfficeAccountInfo))
        threaded_run.start()
        return ""
        # messagelist = env['send_message'].reply_qy_message(content, fromUser, toUser, wxOfficeAccountInfo)
        # if len(messagelist) > 0:
        #     print 'test'
        #     for i in range(len(messagelist)):
        #         #print messagelist[i]
        #         #if i > 0:
        #         env['send_message'].send_qy_custommessage(messagelist[i],wxOfficeAccountInfo['wx_qyh_app_id'])
        #     return ""
        #     #return messagelist[0]
        # else:
        #     return ""
        # pass

    def accept_message(self, cr, uid, messageType, vals, context):
        try:
            if messageType == "wx.image_message_record":
                return self.create_image_record(cr, uid, vals, context)
            elif messageType == "wx.voice_message_record":
                return self.create_voice_record(cr, uid, vals, context)
            elif messageType == "wx.link_message_record":
                return self.create_link_record(cr, uid, vals, context)
            elif messageType == "wx.location_message_record":
                return self.create_location_record(cr, uid, vals, context)
            elif messageType == "wx.video_message_record":
                return self.create_video_record(cr, uid, vals, context)
            elif messageType == "wx.message_text":
                return self.create_text_record(cr, uid, vals, context)
            pass
        except Exception as e:
            _logger.info("接受消息出错:" + str(e))

    def create_image_record(self, cr, uid, vals, context):
        imageId = vals["MediaId"]
        fromUser = vals['FromUserName']
        toUser = vals['ToUserName']
        msgid = vals['MsgId']
        picurl = vals['PicUrl']
        createTime = (int)(vals['CreateTime'])
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        imagedata = urllib2.urlopen(picurl).read()
        imagedata_encode = base64.b64encode(imagedata)
        env = Environment(cr, uid, context)
        # from yuancloud.addons.ycloud_wx import ycloud_wx_customer as wx_customer
        # wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(cr, uid, context)
        # values = {}
        # values['openid'] = fromUser
        # values['officialaccount_id'] = toUser
        # wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        data = {}
        data.update({
            'message_msgid': msgid,
            'message_event': 'receive',
            'official_username':"", #wx_customerinfo.id,
            'message_picurl': picurl,
            'message_mediaId': imageId,
            'message_imagedata': imagedata_encode,
            'createTime': createtime,
            'message_status': 'use_sucess',
            'officialaccount': wxOfficeAccountInfo['id']
        })
        try:
            create_result = env['wx.image_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入图片消息失败:' + str(e))
            print e
        return ""

    def create_voice_record(self, cr, uid, vals, context):
        fromUser = vals['FromUserName']
        toUser = vals['ToUserName']
        recognitionInfo = ""

        if 'Recognition' in vals:
            recognitionInfo = vals["Recognition"]
        format_value = vals['Format']
        mediaId = vals['MediaId']
        voicedata = ""
        env = Environment(cr, uid, context)
        from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
        wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(cr, uid, context)
        values = {}
        values['openid'] = fromUser
        values['officialaccount_id'] = toUser
        wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                   wxOfficeAccountInfo['wx_appsecret'])
        # 判断字符串为空
        audio_format, media_info = mediaManager.get_media(mediaId)
        # print audio_format
        # filename = fromUser + "." + format_value
        # new_head_url = os.path.join(os.getcwd(), filename)
        # print new_head_url
        # f = open(new_head_url, "w+b")
        # f.write(media_info)
        # f.close()
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime((int)(vals['CreateTime'])))
        print createtime
        msgid = vals['MsgId']
        data = {}
        data.update({
            'message_msgid': msgid,
            'message_event': 'receive',
            'official_username': wx_customerinfo.id,
            'message_format': format_value,
            'message_mediaId': mediaId,
            'message_recognition': recognitionInfo,
            'message_voicedata': base64.b64encode(media_info),
            'createTime': createtime,
            'message_status': 'use_sucess',
            'officialaccount': wxOfficeAccountInfo['id']
        })
        try:
            create_result = env['wx.voice_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入语音消息失败:' + str(e))
            print e

        pass

    def create_link_record(self, cr, uid, vals, context):
        fromUser = vals['FromUserName']
        toUser = vals['ToUserName']
        linktitle = vals["Title"]
        linkdescription = vals["Description"]
        linkurl = vals["Url"]
        createTime = (int)(vals['CreateTime'])
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        msgid = vals['MsgId']
        env = Environment(cr, uid, context)
        from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
        wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(cr, uid, context)
        values = {}
        values['openid'] = fromUser
        values['officialaccount_id'] = toUser
        wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        data = {}
        data.update({
            'message_msgid': msgid,
            'message_event': 'receive',
            'official_username': wx_customerinfo.id,
            'message_title': linktitle,
            'message_description': linkdescription,
            'message_url': linkurl,
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status': 'use_sucess'
        })
        try:
            create_result = env['wx.link_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入链接消息失败:' + str(e))
            print e
        pass

    def create_location_record(self, cr, uid, jsonStr, context):
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        locationX = jsonStr["Location_X"]
        locationY = jsonStr["Location_Y"]
        scale = jsonStr["Scale"]
        label = jsonStr["Label"]
        createTime = (int)(jsonStr['CreateTime'])
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        msgid = jsonStr['MsgId']
        env = Environment(cr, uid, context)
        from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
        wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(cr, uid, context)
        values = {}
        values['openid'] = fromUser
        values['officialaccount_id'] = toUser
        wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        data = {}
        data.update({
            'message_msgid': msgid,
            'message_event': 'receive',
            'official_username': wx_customerinfo.id,
            'message_locationX': locationX,
            'message_locationY': locationY,
            'message_scale': scale,
            'message_label': label,
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status': 'use_sucess'
        })
        try:
            create_result = env['wx.location_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入位置消息失败:' + str(e))
            print e

    def create_video_record(self, cr, uid, jsonStr, context):
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        thumbMediaId = jsonStr["ThumbMediaId"]
        mediaId = jsonStr["MediaId"]
        env = Environment(cr, uid, context)
        from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
        wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(cr, uid, context)
        values = {}
        values['openid'] = fromUser
        values['officialaccount_id'] = toUser
        wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                   wxOfficeAccountInfo['wx_appsecret'])
        # 判断字符串为空
        video_format, media_info = mediaManager.get_video(mediaId)
        # if video_format == "video/mpeg4":
        #    video_format = ".mp4"
        # filename = fromUser + mediaId + video_format
        # print filename
        # new_head_url = os.path.join(os.getcwd(), filename)
        # print new_head_url
        # f = open(new_head_url, "w+b")
        # f.write(media_info)
        # f.close()

        thumb_video_format, thumb_media_info = mediaManager.get_video(thumbMediaId)
        # if thumb_video_format == "image/jpeg":
        #    thumb_video_format = ".jpg"
        # thumb_filename = fromUser + thumbMediaId + thumb_video_format
        # print thumb_filename
        # new_thumb_head_url = os.path.join(os.getcwd(), thumb_filename)
        # print new_thumb_head_url
        # f = open(new_thumb_head_url, "w+b")
        # f.write(thumb_media_info)
        # f.close()
        msgid = jsonStr['MsgId']
        createTime = (int)(jsonStr['CreateTime'])
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data = {}
        data.update({
            'message_msgid': msgid,
            'message_event': 'receive',
            'official_username': wx_customerinfo.id,
            'message_videodata': base64.b64encode(media_info),
            'message_mediaId': mediaId,
            'message_description': "",
            'message_thumbMediaId': thumbMediaId,
            'message_thumbMediadata': base64.b64encode(thumb_media_info),
            'message_title': "",
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status': 'use_sucess'
        })
        try:
            create_result = env['wx.video_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入短视频消息失败:' + str(e))
            print e

    def create_text_record(self, cr, uid, jsonStr, context):
        content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        MsgId = jsonStr['MsgId']
        env = Environment(cr, uid, context)
        wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        text_template = {}
        text_template.update({
            "id": ""
        })
        try:
            env['send_message'].insert_text_record(fromUser, wxOfficeAccountInfo, env, content, text_template, "",
                                                   False, MsgId, 'use_sucess', 'receive')
        except Exception as e:
            _logger.info("插入文本消息记录出错:" + str(e))
        threaded_run = threading.Thread(target=self.processmessage,
                                        args=(fromUser, cr, uid, context, content, wxOfficeAccountInfo))
        threaded_run.start()
        cr.commit()
        return ""
        #messagelist = env['send_message'].reply_message(content, fromUser, toUser, wxOfficeAccountInfo)
        #if len(messagelist) > 0:
        #    for i in range(len(messagelist)):
        #        if i > 0:
        #            env['send_message'].sendcustommessage(messagelist[i])
        #    return messagelist[0]
        #else:
        #    return ""

    def processmessage(self, openid, cr, uid, context, content, wxOfficeAccountInfo):
        dbname = cr.dbname
        uid = uid
        context = context.copy()
        with api.Environment.manage():
            with registry(dbname).cursor() as new_cr:
                context.update({
                    "openid":openid
                })
                env = Environment(new_cr, uid, context)
                wxOfficeAccountInfo=env['wx.officialaccount'].search([('id','=',wxOfficeAccountInfo.id)])
                #currentContext={}
                model_instances = []
                model_instance = {}
                model_instance.update({
                    "id":"",
                    "model_value": ""
                    })
                model_instances.append(model_instance)
                env['wx.message.send_event'].sendmessage_TriggeredbyCommand(content,model_instances,wxOfficeAccountInfo)
                # contents = content.split(' ')
                # message_define = env['wx.message_define'].search(
                #     [('message_command', '=', contents[0]), ('officialaccount', '=', wxOfficeAccountInfo['id'])])
                # if len(message_define) > 0:
                #     message_define_value = message_define[0]
                #     model_info = message_define_value['model_id']['model']
                #     message_method = message_define_value['message_method']
                #     template_code = message_define_value['message_template_code']
                #     template_type = message_define_value['message_template_type']
                #     message_process_mode = message_define_value['message_process_mode']
                #     limit = 1
                #     if message_process_mode == "list":
                #         limit = 5
                #     else:
                #         limit = 1
                #     model_values = ""
                #     model_instances = []
                #     if message_method == False or message_method == "":
                #         model_values = env[model_info].search([], limit=limit)
                #         for model_value in model_values:
                #             model_instance = {}
                #             model_instance.update({
                #                 "id": message_define_value['model_id']['id'],
                #                 "model_value": model_value
                #             })
                #             model_instances.append(model_instance)
                #     else:
                #         print message_method
                #         model_values = getattr(env[model_info], message_method)(env, contents, openid)
                #     print model_values
                #
                #     if message_define_value['is_message_reply']:
                #         env['send_message'].sendMessage(template_code, template_type, model_instances, openid,
                #                                         wxOfficeAccountInfo)
                #         pass

    def process_clickkey(self, cr, uid, key, jsonStr, context):
        content = ""
        # if 'EventKey' in jsonStr:
        #     content = jsonStr['EventKey']
        #     if content=="":
        #         content=key
        # else:
        #     content = key
        content=key
        print content
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        env = Environment(cr, uid, context)
        if 'AgentID' in jsonStr:
            agentID=jsonStr['AgentID']
            wxOfficeAccountInfo = env['wx.officialaccount'].getqyhofficialaccount(toUser,agentID)
        else:
            wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
        text_template = {}
        text_template.update({
            "id": ""
        })
        #self.processmessage(fromUser,cr,uid,context, content, wxOfficeAccountInfo)
        threaded_run = threading.Thread(target=self.processmessage,
                                        args=(fromUser, cr, uid, context, content, wxOfficeAccountInfo))
        threaded_run.start()
        return ""
        # messagelist = env['send_message'].reply_message(content, fromUser, toUser, wxOfficeAccountInfo)
        # if len(messagelist) > 0:
        #     for i in range(len(messagelist)):
        #         if i > 0:
        #             env['send_message'].sendcustommessage(messagelist[i])
        #     if content == "service":
        #         return env['send_message'].reply_service_message(fromUser, toUser)
        #     elif directsend:
        #         env['send_message'].sendcustommessage(messagelist[0])
        #     else:
        #         return messagelist[0]
        # else:
        #     return ""


