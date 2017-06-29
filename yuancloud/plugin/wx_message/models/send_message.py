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
from yuancloud.tools.translate import _ as translate
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
from yuancloud.addons.wx_base.sdks.enterpriseaccount_sdk import message_manager
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import media_manager
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import template_manager
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
from yuancloud.addons.wx_base.sdks.openplatform_sdk import public_sdk
from yuancloud.addons.wx_base.sdks.openplatform_sdk import qy_open_public_sdk
import xmltodict
from urllib import urlencode, quote as quote
import datetime
import dateutil.relativedelta as relativedelta
import lxml
import urlparse
from yuancloud import cache
from yuancloud import tools, api
_logger = logging.getLogger(__name__)
try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,
        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")

class send_message(models.AbstractModel):
    def replacecontent(self,content,model,user=None,context=None):
        template=content
        try:
            template = mako_template_env.from_string(tools.ustr(content))
        except Exception:
            _logger.exception("Failed to load template %r", template)
            return content
        variables={}
        render_result=content
        variables['ctx']=context
        variables['user']=user
        variables['object'] = model
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.exception("Failed to render template %r using values %r" % (template, variables))
            render_result = content
        return render_result
    def reply_qy_message(self,cr,uid,content, fromUser, toUser, wxOfficeAccountInfo,context):
        result=[]
        env = Environment(cr, uid, context)
        tx_ids = env['wx.message_subscribe'].search([('message_key', '=', content),('officialaccount','=',wxOfficeAccountInfo['id'])])
        messageinfo = reply_information.reply_information()
        if len(tx_ids) > 0:
            for tx_message in tx_ids:
                print tx_message
                typecode = tx_message['message_type']['typecode']
                print typecode
                if typecode == "text":
                    content = tx_message['message_text']['message_content']
                    print content
                    self.insert_qy_text_record(fromUser,wxOfficeAccountInfo,env,content,tx_message['message_text'],"",False,"","sending","send")
                    result.append(messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), content))
                elif typecode == "image":
                    imagedata = tx_message['message_image']['message_imagedata']
                    im = imagedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                                wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('image', im, '.png')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.image_reply_xml(fromUser, toUser, int(time.time()), media_id))
                elif typecode == "voice":
                    voicedata = tx_message['message_voice']['message_voicedata']
                    im = voicedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('voice', im, '.amr')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.audio_reply_xml(fromUser, toUser, int(time.time()), media_id))
                elif typecode == "imagetext":
                    mpnews = tx_message['message_mpnews_content']['message_news']
                    messages = []
                    pic_url=tx_message['message_mpnews_content']['message_picurl']
                    imagedata = tx_message['message_mpnews_content']['message_imagedata']
                    message_title=tx_message['message_mpnews_content']['message_title']
                    message_description=tx_message['message_mpnews_content']['message_description']
                    message_url=tx_message['message_mpnews_content']['message_url']
                    message=self.mk_mpnews(pic_url,imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                    tx_message['message_mpnews_content']['message_picurl'] = message['picurl']
                    message.update({
                            "id":""
                        })
                    messages.append(message)
                    for i in (mpnews):
                        message = self.mk_mpnews(i['message_picurl'],i['message_imagedata'],i['message_title'],i['message_description'],i['message_url'],wxOfficeAccountInfo)
                        message.update({
                            "id":""
                            })
                        i['message_picurl'] = message['picurl']
                        messages.append(message)
                    self.insert_mpnews_record(fromUser,wxOfficeAccountInfo,env,messages,tx_message['message_mpnews_content'],"",False)
                    result.append(messageinfo.news_reply_xml(fromUser, toUser, int(time.time()), messages))
                elif typecode == "music":
                    music = tx_message['message_music']
                    musicTitle = music['message_title']
                    musicDesc = music['message_description']
                    musicUrl = music['message_musicURL']
                    HQMusicUrl = music['message_HQMusicUrl']
                    imagedata = music['message_ThumbMediaData']
                    im = imagedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('image', im, '.jpg')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.music_reply_xml(fromUser, toUser, int(time.time()), musicTitle, musicDesc,
                                                           musicUrl, HQMusicUrl, media_id))
                elif typecode == "template":
                    print "template"
                    model_values=[]
                    model_value={}
                    model_value.update({
                        "id":"",
                        "model_value":""
                    })
                    model_values.append(model_value)
                    self.send_template_message(cr,uid,tx_message['message_template']['template_code'],model_values,fromUser,wxOfficeAccountInfo,context)
                    result.append("")
                elif typecode == "video":
                    video = tx_message['message_video']
                    video_title = video['message_title']
                    video_desc = video['message_description']
                    video_data = video['message_videodata']
                    im = video_data.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('video', im, '.mp4')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.audio_reply_xml(fromUser, toUser, int(time.time()), media_id))
        return result
    def send_qy_custommessage(self,messagelist,agentid):
        try:
            if messagelist=="":
                return
            print messagelist
            json=xmltodict.parse((messagelist))['xml']
            userid=json['ToUserName']
            fromusername=json['FromUserName']
            MsgType=json['MsgType']
            env = Environment(self._cr, self._uid, self._context)
            wxOfficeAccountInfo = env['wx.officialaccount'].search(
            [('wx_appid', '=', fromusername), ('wx_qyh_app_id', '=', agentid)])[0]
            appid=wxOfficeAccountInfo['wx_appid']
            appsercret=wxOfficeAccountInfo['wx_appsecret']
            customManager = message_manager.message_manager(appid,appsercret)
            if MsgType=="text":
                render_result=json['Content']
                customManager.sendtextmessage(wxOfficeAccountInfo['wx_qyh_app_id'],render_result,userid,"","",False)
            elif MsgType=="image":
                media_id=json['Image']['MediaId']
                #customManager.sendImage_custommessage(userid,media_id,"")
                #todo
            elif MsgType=="news":
                Articles=json['Articles']
                articles_info=[]
                print Articles
                if json['ArticleCount']=="1":
                    article={}
                    article.update({
                        'title':Articles['item']['Title'],
                        'description':Articles['item']['Description'],
                        'url':Articles['item']['Url'],
                        'picurl':Articles['item']['PicUrl']
                    })
                    articles_info.append(article)
                    #return customManager.sendnews_custommessage(openid,articles_info,"")
                for art in Articles['item']:
                    article={}
                    article.update({
                        'title':art['Title'],
                        'description':art['Description'],
                        'url':art['Url'],
                        'picurl':art['PicUrl']
                    })
                    articles_info.append(article)
                #customManager.sendnews_custommessage(openid,articles_info,"")
                #todo
        except Exception as e:
            _logger.info("发送企业号消息出错:"+str(e))
    def sendcustommessage(self,messagelist):
        try:
            if messagelist=="":
                return
            print messagelist
            json=xmltodict.parse((messagelist))['xml']
            openid=json['ToUserName']
            fromusername=json['FromUserName']
            MsgType=json['MsgType']
            env = Environment(self._cr, self._uid, self._context)
            wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(fromusername)
            customManager = custom_manager.custom_manager(wxOfficeAccountInfo["wx_appid"],wxOfficeAccountInfo["wx_appsecret"])
            if MsgType=="text":
                render_result=json['Content']
                customManager.sendText_custommessage(openid,render_result,"")
            elif MsgType=="image":
                media_id=json['Image']['MediaId']
                customManager.sendImage_custommessage(openid,media_id,"")
            elif MsgType=="news":
                Articles=json['Articles']
                articles_info=[]
                print Articles
                if json['ArticleCount']=="1":
                    article={}
                    article.update({
                        'title':Articles['item']['Title'],
                        'description':Articles['item']['Description'],
                        'url':Articles['item']['Url'],
                        'picurl':Articles['item']['PicUrl']
                    })
                    articles_info.append(article)
                    return customManager.sendnews_custommessage(openid,articles_info,"")
                for art in Articles['item']:
                    article={}
                    article.update({
                        'title':art['Title'],
                        'description':art['Description'],
                        'url':art['Url'],
                        'picurl':art['PicUrl']
                    })
                    articles_info.append(article)
                customManager.sendnews_custommessage(openid,articles_info,"")
        except Exception as e:
            _logger.info("发送客服消息出错:"+str(e))
    def mk_mpnews(self,pic_url,imagedata,message_title,message_description,message_url,wxOfficeAccountInfo):
        message={}
        if pic_url=="False":
            if imagedata=="False":
                message.update({
                    'title': message_title,
                    'description': message_description,
                    'picurl': "",
                    'url': message_url
                    })
            else:
                im = imagedata.decode('base64')
                mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                                           wxOfficeAccountInfo['wx_appsecret'])
                uploadresult = mediaManager.upload_image(im, ".jpg")
                print uploadresult
                if 'url' in uploadresult:
                    url = uploadresult['url']
                    message.update({
                        'title': message_title,
                        'description': message_description,
                        'picurl': url,
                        'url': message_url
                        })
                else:
                    message.update({
                    'title': message_title,
                    'description': message_description,
                    'picurl': "",
                    'url': message_url
                    })
        else:
            message.update({
                    'title': message_title,
                    'description': message_description,
                    'picurl': pic_url,
                    'url': message_url
                    })
        return message
    def reply_service_message(self,fromUser,toUser):
        messageinfo = reply_information.reply_information()
        return messageinfo.serice_reply_xml(fromUser,toUser,int(time.time()))
    def reply_message(self,cr,uid,content, fromUser, toUser, wxOfficeAccountInfo,context):
        result=[]
        env = Environment(cr, uid, context)
        tx_ids = env['wx.message_subscribe'].search([('message_key', '=', content),('officialaccount','=',wxOfficeAccountInfo['id'])])
        messageinfo = reply_information.reply_information()
        if len(tx_ids) > 0:
            for tx_message in tx_ids:
                print tx_message
                typecode = tx_message['message_type']['typecode']
                print typecode
                if typecode == "text":
                    content = tx_message['message_text']['message_content']
                    print content
                    self.insert_text_record(fromUser,wxOfficeAccountInfo,env,content,tx_message['message_text'],"",False,"","sending","send")
                    result.append(messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), content))
                elif typecode == "image":
                    imagedata = tx_message['message_image']['message_imagedata']
                    im = imagedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                                wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('image', im, '.png')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.image_reply_xml(fromUser, toUser, int(time.time()), media_id))
                elif typecode == "voice":
                    voicedata = tx_message['message_voice']['message_voicedata']
                    im = voicedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('voice', im, '.amr')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.audio_reply_xml(fromUser, toUser, int(time.time()), media_id))
                elif typecode == "imagetext":
                    mpnews = tx_message['message_mpnews_content']['message_news']
                    messages = []
                    pic_url=tx_message['message_mpnews_content']['message_picurl']
                    imagedata = tx_message['message_mpnews_content']['message_imagedata']
                    message_title=tx_message['message_mpnews_content']['message_title']
                    message_description=tx_message['message_mpnews_content']['message_description']
                    message_url=tx_message['message_mpnews_content']['message_url']
                    message=self.mk_mpnews(pic_url,imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                    tx_message['message_mpnews_content']['message_picurl'] = message['picurl']
                    message.update({
                            "id":""
                        })
                    messages.append(message)
                    for i in (mpnews):
                        message = self.mk_mpnews(i['message_picurl'],i['message_imagedata'],i['message_title'],i['message_description'],i['message_url'],wxOfficeAccountInfo)
                        message.update({
                            "id":""
                            })
                        i['message_picurl'] = message['picurl']
                        messages.append(message)
                    self.insert_mpnews_record(fromUser,wxOfficeAccountInfo,env,messages,tx_message['message_mpnews_content'],"",False)
                    result.append(messageinfo.news_reply_xml(fromUser, toUser, int(time.time()), messages))
                elif typecode == "music":
                    music = tx_message['message_music']
                    musicTitle = music['message_title']
                    musicDesc = music['message_description']
                    musicUrl = music['message_musicURL']
                    HQMusicUrl = music['message_HQMusicUrl']
                    imagedata = music['message_ThumbMediaData']
                    im = imagedata.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('image', im, '.jpg')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.music_reply_xml(fromUser, toUser, int(time.time()), musicTitle, musicDesc,
                                                           musicUrl, HQMusicUrl, media_id))
                elif typecode == "template":
                    print "template"
                    model_values=[]
                    model_value={}
                    model_value.update({
                        "id":"",
                        "model_value":""
                    })
                    model_values.append(model_value)
                    self.send_template_message(cr,uid,tx_message['message_template']['template_code'],model_values,fromUser,wxOfficeAccountInfo,context)
                    result.append("")
                elif typecode == "video":
                    video = tx_message['message_video']
                    video_title = video['message_title']
                    video_desc = video['message_description']
                    video_data = video['message_videodata']
                    im = video_data.decode('base64')
                    mediaManager = media_manager.media_manager(wxOfficeAccountInfo['wx_appid'],
                                                               wxOfficeAccountInfo['wx_appsecret'])
                    uploadresult = mediaManager.upload_media('video', im, '.mp4')
                    print uploadresult
                    if 'errcode' not in uploadresult:
                        media_id = uploadresult['media_id']
                        result.append(messageinfo.audio_reply_xml(fromUser, toUser, int(time.time()), media_id))
        return result
    def send_qy_text_message(self,cr,uid,template_code,model_values,userid,wxOfficeAccountInfo,event_entity_id=0,context=None):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.text_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            if len(model_values)>1:
                totalcontent=""
                i=1
                association_order=[]
                for model in model_values:
                    content=self.replacecontent(text_template['message_content'],model['model_value'],user,context)
                    totalcontent=totalcontent+str(i)+":"+content
                    i=i+1
                    if 'id' in model['model_value']:
                        association_order.append({
                            "id":model['model_value']['id']
                        })
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    key = wxOfficeAccountInfo['third_auth_SuiteId'] + "suite_access_token"
                    suite_access_token=cache.redis.get(key)
                    access_token=qy_open_public_sdk.get_corp_access_token(suite_access_token,wxOfficeAccountInfo['third_auth_SuiteId'],wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['third_auth_code'])
                    message_manager.sendtextmessage_access_token(wxOfficeAccountInfo['wx_qyh_app_id'],totalcontent,userid,"","",False,access_token)
                    pass
                else:
                    customManager = message_manager.message_manager(appid,appsercret)
                    customManager.sendtextmessage(wxOfficeAccountInfo['wx_qyh_app_id'],totalcontent,userid,"","",False)
                userlist=userid.split('|')
                for user in userlist:
                    self.insert_qy_text_record(user,wxOfficeAccountInfo,env,content,text_template,json.dumps(association_order),False,"","sending","send",event_entity_id)
            else:
                model=model_values[0]['model_value']
                content=self.replacecontent(text_template['message_content'],model,user,context)
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                association_order=[]
                if 'id' in model:
                    association_order.append({
                            "id":model['id']
                        })
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    key = wxOfficeAccountInfo['third_auth_SuiteId'] + "suite_access_token"
                    suite_access_token=cache.redis.get(key)
                    access_token=qy_open_public_sdk.get_corp_access_token(suite_access_token,wxOfficeAccountInfo['third_auth_SuiteId'],wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['third_auth_code'])
                    message_manager.sendtextmessage_access_token(wxOfficeAccountInfo['wx_qyh_app_id'],content,userid,"","",False,access_token)
                    pass
                else:
                    customManager = message_manager.message_manager(appid,appsercret)
                    customManager.sendtextmessage(wxOfficeAccountInfo['wx_qyh_app_id'],content,userid,"","",False)
                userlist=userid.split('|')
                for user in userlist:
                    self.insert_qy_text_record(user,wxOfficeAccountInfo,env,content,text_template,json.dumps(association_order),False,"","sending","send",event_entity_id)
        pass
    def send_qy_message(self,cr,uid,userid,model_instance,eventKey,context,event_entity_id=0):
        env = Environment(cr, uid, context)
        tx_ids = env['wx.message_subscribe'].search([('message_key', '=', eventKey)])
        if len(tx_ids) > 0:
            for tx_message in tx_ids:
                typecode = tx_message['message_type']['typecode']
                print typecode
                if typecode == "text":
                    self.send_qy_text_message(cr,uid,tx_message['message_text']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                elif typecode == "image":
                    self.send_image_message(cr,uid,tx_message['message_image']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                    pass
                elif typecode == "voice":
                    self.send_qy_mpnews_message(cr,uid,tx_message['message_voice']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                    pass
                elif typecode == "imagetext":
                    self.send_qy_mpnews_message(cr,uid,tx_message['message_mpnews_content']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                    pass
                elif typecode == "music":
                    self.send_music_message(cr,uid,tx_message['message_music']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                    pass
                elif typecode == "template":
                    self.send_template_message(cr,uid,tx_message['message_template']['template_code'],model_instance,userid,tx_message['officialaccount'],context)
                    pass
                elif typecode == "video":
                    self.send_video_message(cr,uid,tx_message['message_video']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
        pass
    def sendMessage4Instances(self,cr,uid,eventKey,models_instances,openid,wxOfficeAccountInfo,context):
        env = Environment(cr, uid, context)
        tx_ids = env['wx.message_subscribe'].search([('message_key', '=', eventKey),('officialaccount','=',wxOfficeAccountInfo['id'])])
        if len(tx_ids) > 0:
            for tx_message in tx_ids:
                typecode = tx_message['message_type']['typecode']
                print typecode
                if typecode == "text":
                    self.send_text_message(cr,uid,tx_message['message_text']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                elif typecode == "image":
                    self.send_image_message(cr,uid,tx_message['message_image']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
                elif typecode == "voice":
                    self.send_voice_message(cr,uid,tx_message['message_voice']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
                elif typecode == "imagetext":
                    self.send_mpnews_message(cr,uid,tx_message['message_mpnews_content']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
                elif typecode == "music":
                    self.send_music_message(cr,uid,tx_message['message_music']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
                elif typecode == "template":
                    self.send_template_message(cr,uid,tx_message['message_template']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
                elif typecode == "video":
                    self.send_video_message(cr,uid,tx_message['message_video']['template_code'],models_instances,openid,wxOfficeAccountInfo,context)
                    pass
        pass
    def sendMessage(self,cr,uid,template_code,template_type,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context):
        _logger.info("template_code:"+template_code)
        _logger.info("template_type.typecode:"+template_type.typecode)
        _logger.info("openid:"+openid)
        if template_type.typecode=="text":
            if wxOfficeAccountInfo.is_qyhapp:
                self.send_qy_text_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
                pass
            else:
                self.send_text_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="image":
            self.send_image_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="imagetext":
            if wxOfficeAccountInfo.is_qyhapp:
                self.send_qy_mpnews_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
                pass
            else:
                self.send_mpnews_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="voice":
            self.send_voice_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="video":
            self.send_video_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="location":
            self.send_location_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="link":
            self.send_link_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="music":
            self.send_music_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="template":
            self.send_template_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        elif template_type.typecode=="list":
            self.send_list_message(cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
        else:
            pass

    def send_list_message(self,cr,uid,template_code,model_instances,openid,wxOfficeAccountInfo,event_entity_id,context):
        env = Environment(cr, uid, context)
        _logger.info("准备发送列表消息")
        list_templates=env['list.message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(list_templates)>0:
            list_template=list_templates[0]
            _logger.info("列表消息类型:"+list_template['message_template_type'].typecode)
            if list_template['message_template_type'].typecode=="text":
                if wxOfficeAccountInfo.is_qyhapp:
                    self.send_qy_text_message(cr,uid,list_template['message_template_code'],model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
                else:
                    self.send_text_message(cr,uid,list_template['message_template_code'],model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
            elif list_template['message_template_type'].typecode=="imagetext":
                if wxOfficeAccountInfo.is_qyhapp:
                    self.send_qy_mpnews_message(cr,uid,list_template['message_template_code'],model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
                else:
                    self.send_mpnews_message(cr,uid,list_template['message_template_code'],model_instances,openid,wxOfficeAccountInfo,event_entity_id,context)
            else:
                _logger.info("列表消息配置无效的消息模板")
        else:
            pass

    def send_text_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.text_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            if len(model_values)>1:
                totalcontent=""
                i=1
                association_order=[]
                for model in model_values:
                    content=self.replacecontent(text_template['message_content'],model['model_value'],user,context)
                    totalcontent=totalcontent+str(i)+":"+content
                    i=i+1
                    if 'id' in model['model_value']:
                        association_order.append({
                            "id":model['model_value']['id']
                        })
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    custom_manager.sendText_custommessage_access_token(openid,totalcontent,"",auth_access_token)
                    pass
                else:
                    customManager = custom_manager.custom_manager(appid,appsercret)
                    customManager.sendText_custommessage(openid,totalcontent,"")
                self.insert_text_record(openid,wxOfficeAccountInfo,env,totalcontent,text_template,json.dumps(association_order),True,"","sending","send",event_entity_id)
            else:
                model=model_values[0]['model_value']
                content=self.replacecontent(text_template['message_content'],model,user,context)
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                association_order=[]
                if 'id' in model:
                    association_order.append({
                            "id":model['id']
                        })
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    print auth_access_token
                    custom_manager.sendText_custommessage_access_token(openid,content,"",auth_access_token)
                    pass
                else:
                    customManager = custom_manager.custom_manager(appid,appsercret)
                    customManager.sendText_custommessage(openid,content,"")
                self.insert_text_record(openid,wxOfficeAccountInfo,env,content,text_template,json.dumps(association_order),False,"","sending","send",event_entity_id)
        else:
            pass
        pass
    def insert_text_record(self,openid,wxOfficeAccountInfo,env,totalcontent,text_template,association_order,islist,message_msgid,message_status,message_event,event_entity_id=0):
        data = {}
        wx_customer=env['wx.customer'].search([('openid','=',openid)])
        wx_userid=0
        if wx_customer:
            wx_userid=wx_customer[0].id
        else:
            from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
            wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(env.cr, env.uid, env.context)
            values = {}
            values['openid'] = openid
            values['officialaccount_id'] = wxOfficeAccountInfo['wx_id']
            wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
            wx_userid=wx_customerinfo.id
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'official_username':wx_userid,
            'isList':islist,
            'message_event': message_event,
            'message_content': totalcontent,
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status':message_status,
            'message_template':text_template['id'],
            'association_order':association_order,
            'message_msgid':message_msgid,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.text_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入消息失败:' + str(e))
            print e
    def insert_qy_text_record(self,openid,wxOfficeAccountInfo,env,totalcontent,text_template,association_order,islist,message_msgid,message_status,message_event,event_entity_id=0):
        data = {}
        employee_id=0
        try:
            user_id=env['res.users'].search([('login','=',openid)])[0]['id']
            employee_id=env['hr.employee'].search([('user_id','=',user_id)])[0]['id']
        except Exception as e:
            employee_id=0
        if employee_id==0:
            return
        print employee_id
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'qy_toUserName': employee_id,
            'isList':islist,
            'message_event': message_event,
            'message_content': totalcontent,
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status':message_status,
            'message_template':text_template['id'],
            'association_order':association_order,
            'message_msgid':message_msgid,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.text_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入企业号消息失败:' + str(e))
            print e
    def send_image_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        pass

    def send_qy_mpnews_message(self,cr,uid,template_code,model_values,userid,wxOfficeAccountInfo,event_entity_id=0,context=None):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.mpnews_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            if len(model_values)>1:
                association_order=[]
                messagesinfo=[]
                message_records=[]
                #qrmodel = model_values.filtered(lambda r: r.id == text_template['model_id'])[0]
                main_value={}
                for model in model_values:
                    if model['id']==text_template['model_id']['id']:
                        main_value=model['model_value']
                message_title=self.replacecontent(text_template['message_title'],main_value,user,context)
                message_description=self.replacecontent(text_template['message_description'],main_value,user,context)
                message_picurl=self.replacecontent(text_template['message_picurl'],main_value,user,context)
                message_url=self.replacecontent(text_template['message_url'],main_value,user,context)
                message_imagedata=self.replacecontent(text_template['message_imagedata'],main_value,user,context)
                message=self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                #text_template['message_picurl'] = message['picurl']
                messagesinfo.append(message)
                message.update({
                    "id":""
                })
                message_records.append(message)
                mpnews = text_template['message_news']
                for model in model_values:
                    for i in (mpnews):
                        if model['id']==i['model_id']['id']:
                            message_title=translate(self.replacecontent(i['message_title'],model['model_value'],user,context))
                            message_description=self.replacecontent(i['message_description'],model['model_value'],user,context)
                            message_picurl=self.replacecontent(i['message_picurl'],model['model_value'],user,context)
                            message_url=self.replacecontent(i['message_url'],model['model_value'],user,context)
                            message_imagedata=self.replacecontent(i['message_imagedata'],model['model_value'],user,context)
                            message = self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                            #i['message_picurl'] = message['picurl']
                            messagesinfo.append(message)
                            message.update({
                                "id":model['id']
                            })
                            message_records.append(message)
                    if 'id' in model['model_value']:
                        association_order.append({
                            "id":model['model_value']['id']
                        })
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']

                if wxOfficeAccountInfo.is_auth_officialaccount:
                    key = wxOfficeAccountInfo['third_auth_SuiteId'] + "suite_access_token"
                    suite_access_token=cache.redis.get(key)
                    access_token=qy_open_public_sdk.get_corp_access_token(suite_access_token,wxOfficeAccountInfo['third_auth_SuiteId'],wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['third_auth_code'])
                    message_manager.sendtextmessage_access_token(wxOfficeAccountInfo['wx_qyh_app_id'],message_records,userid,"","",False,access_token)
                    pass
                else:
                    customManager = message_manager.message_manager(appid,appsercret)
                    print messagesinfo
                    customManager.sendnewsmessage(wxOfficeAccountInfo['wx_qyh_app_id'],message_records,userid,"","",False)

                userlist=userid.split('|')
                for user in userlist:
                    self.insert_qy_mpnews_record(user,wxOfficeAccountInfo,env,message_records,text_template,json.dumps(association_order),False,event_entity_id)
            else:
                model=model_values[0]
                messagesinfo=[]
                message_records=[]
                #qrmodel = model_values.filtered(lambda r: r.id == text_template['model_id'])[0]
                main_value={}
                for model in model_values:
                    if model['id']==text_template['model_id']['id']:
                        main_value=model['model_value']
                message_title=self.replacecontent(text_template['message_title'],main_value,user,context)
                message_description=self.replacecontent(text_template['message_description'],main_value,user,context)
                message_picurl=self.replacecontent(text_template['message_picurl'],main_value,user,context)
                message_url=self.replacecontent(text_template['message_url'],main_value,user,context)
                message_imagedata=self.replacecontent(text_template['message_imagedata'],main_value,user,context)
                message=self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                #text_template['message_picurl'] = message['picurl']
                messagesinfo.append(message)
                message.update({
                    "id":""
                })
                message_records.append(message)
                mpnews = text_template['message_news']
                for i in (mpnews):
                    message_title=self.replacecontent(i['message_title'],model['model_value'],user,context)
                    message_description=self.replacecontent(i['message_description'],model['model_value'],user,context)
                    message_picurl=self.replacecontent(i['message_picurl'],model['model_value'],user,context)
                    message_url=self.replacecontent(i['message_url'],model['model_value'],user,context)
                    message_imagedata=self.replacecontent(i['message_imagedata'],model['model_value'],user,context)
                    message = self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                    #i['message_picurl'] = message['picurl']
                    messagesinfo.append(message)
                    if 'id' in model['model_value']:
                        message.update({
                            "id":model['model_value']['id']
                        })
                    else:
                        message.update({
                            "id":""
                        })
                    message_records.append(message)
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                association_order=[]
                if 'id' in model:
                    association_order.append({
                            "id":model['id']
                        })
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    key = wxOfficeAccountInfo['third_auth_SuiteId'] + "suite_access_token"
                    suite_access_token=cache.redis.get(key)
                    access_token=qy_open_public_sdk.get_corp_access_token(suite_access_token,wxOfficeAccountInfo['third_auth_SuiteId'],wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['third_auth_code'])
                    message_manager.sendtextmessage_access_token(wxOfficeAccountInfo['wx_qyh_app_id'],message_records,userid,"","",False,access_token)
                    pass
                else:
                    customManager = message_manager.message_manager(appid,appsercret)
                    print messagesinfo
                    customManager.sendnewsmessage(wxOfficeAccountInfo['wx_qyh_app_id'],message_records,userid,"","",False)

                userlist=userid.split('|')
                for user in userlist:
                    self.insert_qy_mpnews_record(user,wxOfficeAccountInfo,env,message_records,text_template,json.dumps(association_order),False,event_entity_id)
        pass

    def send_mpnews_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.mpnews_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            if len(model_values)>1:
                association_order=[]
                messagesinfo=[]
                message_records=[]
                #qrmodel = model_values.filtered(lambda r: r.id == text_template['model_id'])[0]
                main_value={}
                for model in model_values:
                    if model['id']==text_template['model_id']['id']:
                        main_value=model['model_value']
                message_title=self.replacecontent(text_template['message_title'],main_value,user,context)
                message_description=self.replacecontent(text_template['message_description'],main_value,user,context)
                message_picurl=self.replacecontent(text_template['message_picurl'],main_value,user,context)
                message_url=self.replacecontent(text_template['message_url'],main_value,user,context)
                message_imagedata=self.replacecontent(text_template['message_imagedata'],main_value,user,context)
                message=self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                #text_template['message_picurl'] = message['picurl']
                messagesinfo.append(message)
                message.update({
                    "id":""
                })
                message_records.append(message)
                mpnews = text_template['message_news']
                for model in model_values:
                    for i in (mpnews):
                        if model['id']==i['model_id']['id']:
                            message_title=translate(self.replacecontent(i['message_title'],model['model_value'],user,context))
                            message_description=self.replacecontent(i['message_description'],model['model_value'],user,context)
                            message_picurl=self.replacecontent(i['message_picurl'],model['model_value'],user,context)
                            message_url=self.replacecontent(i['message_url'],model['model_value'],user,context)
                            message_imagedata=self.replacecontent(i['message_imagedata'],model['model_value'],user,context)
                            message = self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                            #i['message_picurl'] = message['picurl']
                            messagesinfo.append(message)
                            message.update({
                                "id":model['id']
                            })
                            message_records.append(message)
                    if 'id' in model['model_value']:
                        association_order.append({
                            "id":model['model_value']['id']
                        })
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    custom_manager.sendImage_custommessage_access_token(openid,messagesinfo,"",auth_access_token)
                    pass
                else:
                    customManager = custom_manager.custom_manager(appid,appsercret)
                    customManager.sendnews_custommessage(openid,messagesinfo,"")
                self.insert_mpnews_record(openid,wxOfficeAccountInfo,env,message_records,text_template,json.dumps(association_order),True,event_entity_id)
            else:
                model=model_values[0]
                messagesinfo=[]
                message_records=[]
                #qrmodel = model_values.filtered(lambda r: r.id == text_template['model_id'])[0]
                main_value={}
                for model in model_values:
                    if model['id']==text_template['model_id']['id']:
                        main_value=model['model_value']
                message_title=self.replacecontent(text_template['message_title'],main_value,user,context)
                message_description=self.replacecontent(text_template['message_description'],main_value,user,context)
                message_picurl=self.replacecontent(text_template['message_picurl'],main_value,user,context)
                message_url=self.replacecontent(text_template['message_url'],main_value,user,context)
                message_imagedata=self.replacecontent(text_template['message_imagedata'],main_value,user,context)
                message=self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                text_template['message_picurl'] = message['picurl']
                messagesinfo.append(message)
                message.update({
                    "id":""
                })
                message_records.append(message)
                mpnews = text_template['message_news']
                for i in (mpnews):
                    message_title=self.replacecontent(i['message_title'],model['model_value'],user,context)
                    message_description=self.replacecontent(i['message_description'],model['model_value'],user,context)
                    message_picurl=self.replacecontent(i['message_picurl'],model['model_value'],user,context)
                    message_url=self.replacecontent(i['message_url'],model['model_value'],user,context)
                    message_imagedata=self.replacecontent(i['message_imagedata'],model['model_value'],user,context)
                    message = self.mk_mpnews(message_picurl,message_imagedata,message_title,message_description,message_url,wxOfficeAccountInfo)
                    i['message_picurl'] = message['picurl']
                    messagesinfo.append(message)
                    if 'id' in model['model_value']:
                        message.update({
                            "id":model['model_value']['id']
                        })
                    else:
                        message.update({
                            "id":""
                        })
                    message_records.append(message)
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']
                association_order=[]
                if 'id' in model:
                    association_order.append({
                            "id":model['id']
                        })
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    custom_manager.sendnews_custommessage_access_token(openid,messagesinfo,"",auth_access_token)
                    pass
                else:
                    customManager = custom_manager.custom_manager(appid,appsercret)
                    print messagesinfo
                    customManager.sendnews_custommessage(openid,messagesinfo,"")
                self.insert_mpnews_record(openid,wxOfficeAccountInfo,env,message_records,text_template,json.dumps(association_order),False,event_entity_id)
        else:
            pass
    def insert_mpnews_record(self,openid,wxOfficeAccountInfo,env,messages,mpnews_template,association_order,islist,event_entity_id=0):
        data = {}
        wx_customer=env['wx.customer'].search([('openid','=',openid)])
        wx_userid=0
        if wx_customer:
            wx_userid=wx_customer[0].id
        else:
            from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
            wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(env.cr, env.uid, env.context)
            values = {}
            values['openid'] = openid
            values['officialaccount_id'] = wxOfficeAccountInfo['wx_id']
            wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
            wx_userid=wx_customerinfo.id
        _logger.info("微信客户ID:"+str(wx_userid))
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'official_username': wx_userid,
            'isList':islist,
            'message_event': 'send',
            'message_title':messages[0]['title'],
            'message_description':messages[0]['description'],
            'message_picurl':messages[0]['picurl'],
            'message_url':messages[0]['url'],
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status':'sending',
            'message_template':mpnews_template['id'],
            'association_order':association_order,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.mpnews_message_record'].create(data)
            _logger.info(create_result)
            print create_result
            for message_index in range(1,len(messages)):
                mpnewsinfo={}
                mpnewsinfo.update({
                    "news_id":create_result['id'],
                    "message_title":messages[message_index]['title'],
                    "message_description":messages[message_index]['description'],
                    "message_picurl":messages[message_index]['picurl'],
                    "message_url":messages[message_index]['url'],
                    'model_id':messages[message_index]['id']
                })
                print mpnewsinfo
                create_mpnews_result = env['wx.message_mpnews_record'].create(mpnewsinfo)
        except Exception as e:
            _logger.error('插入图文消息失败:' + str(e))
            print e
    def insert_qy_mpnews_record(self,openid,wxOfficeAccountInfo,env,messages,mpnews_template,association_order,islist,event_entity_id=0):
        data = {}
        employee_id=0
        try:
            user_id=env['res.users'].search([('login','=',openid)])[0]['id']
            employee_id=env['hr.employee'].search([('user_id','=',user_id)])[0]['id']
        except Exception as e:
            employee_id=0
        if employee_id==0:
            return
        print employee_id
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'qy_toUserName': employee_id,
            'isList':islist,
            'message_event': 'send',
            'message_title':messages[0]['title'],
            'message_description':messages[0]['description'],
            'message_picurl':messages[0]['picurl'],
            'message_url':messages[0]['url'],
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status':'sending',
            'message_template':mpnews_template['id'],
            'association_order':association_order,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.mpnews_message_record'].create(data)
            _logger.info(create_result)
            print create_result
            for message_index in range(1,len(messages)):
                mpnewsinfo={}
                mpnewsinfo.update({
                    "news_id":create_result['id'],
                    "message_title":messages[message_index]['title'],
                    "message_description":messages[message_index]['description'],
                    "message_picurl":messages[message_index]['picurl'],
                    "message_url":messages[message_index]['url'],
                    'model_id':messages[message_index]['id']
                })
                print mpnewsinfo
                create_mpnews_result = env['wx.message_mpnews_record'].create(mpnewsinfo)
        except Exception as e:
            _logger.error('插入图文消息失败:' + str(e))
            print e

    def send_voice_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        pass
    def send_video_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        pass
    def send_location_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        pass
    def send_link_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        pass
    def send_music_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.music_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            for modelinfo in model_values:
            # if len(model_values)>1:
            #     totalcontent=""
            #     i=1
            #     association_order=[]
            #     for model in model_values:
            #         content=self.replacecontent(text_template['message_content'],model['model_value'],user,context)
            #         totalcontent=totalcontent+str(i)+":"+content
            #         i=i+1
            #         if 'id' in model['model_value']:
            #             association_order.append({
            #                 "id":model['model_value']['id']
            #             })
            #     appid=wxOfficeAccountInfo['wx_appid']
            #     appsercret=wxOfficeAccountInfo['wx_appsecret']
            #     if wxOfficeAccountInfo.is_auth_officialaccount:
            #         auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
            #         custom_manager.sendText_custommessage_access_token(openid,totalcontent,"",auth_access_token)
            #         pass
            #     else:
            #         customManager = custom_manager.custom_manager(appid,appsercret)
            #         customManager.sendText_custommessage(openid,totalcontent,"")
            #     self.insert_text_record(openid,wxOfficeAccountInfo,env,totalcontent,text_template,json.dumps(association_order),True,"","sending","send",event_entity_id)
            # else:
                model=modelinfo['model_value']#model_values[0]['model_value']
                title=self.replacecontent(text_template['message_title'],model,user,context)
                description=self.replacecontent(text_template['message_description'],model,user,context)
                musicurl=self.replacecontent(text_template['message_musicURL'],model,user,context)
                hqmusicurl=self.replacecontent(text_template['message_HQMusicUrl'],model,user,context)
                thumb_media_id=self.replacecontent(text_template['message_ThumbMediaId'],model,user,context)
                appid=wxOfficeAccountInfo['wx_appid']
                appsercret=wxOfficeAccountInfo['wx_appsecret']

                association_order=[]
                if 'id' in model:
                    association_order.append({
                            "id":model['id']
                        })
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    print auth_access_token
                    custom_manager.sendText_custommessage_access_token(openid,title,description,musicurl,hqmusicurl,thumb_media_id,"",auth_access_token)
                    pass
                else:
                    if str(thumb_media_id)=="False":
                        imagedata=self.replacecontent(text_template['message_ThumbMediaData'],model,user,context)
                        if str(imagedata)<>"False":
                            im = imagedata.decode('base64')
                            mediaManager = media_manager.media_manager(appid,appsercret)
                            uploadresult = mediaManager.upload_media('image', im, '.jpg')
                            print uploadresult
                            if 'errcode' not in uploadresult:
                                thumb_media_id = uploadresult['media_id']
                    customManager = custom_manager.custom_manager(appid,appsercret)
                    customManager.sendMusic_custommesage(openid,title,description,musicurl,hqmusicurl,thumb_media_id,"")
                self.insert_music_record(openid,wxOfficeAccountInfo,env,title,description,musicurl,hqmusicurl,thumb_media_id,text_template,json.dumps(association_order),False,event_entity_id)
        else:
            pass
        pass

    def insert_music_record(self,openid,wxOfficeAccountInfo,env,title,description,musicurl,hqmusicurl,thumb_media_id,music_templete,association_order,msgid,event_entity_id=0):
        data = {}
        wx_customer=env['wx.customer'].search([('openid','=',openid)])
        wx_userid=0
        if wx_customer:
            wx_userid=wx_customer[0].id
        else:
            from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
            wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(env.cr, env.uid, env.context)
            values = {}
            values['openid'] = openid
            values['officialaccount_id'] = wxOfficeAccountInfo['wx_id']
            wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
            wx_userid=wx_customerinfo.id
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'official_username':wx_userid,
            'message_title': title,
            'message_description': description,
            'message_musicURL': musicurl,
            'message_HQMusicUrl': hqmusicurl,
            'message_ThumbMediaId': thumb_media_id,
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_status':'sending',
            'message_template':music_templete['id'],
            'association_order':association_order,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.music_message_record'].create(data)
            _logger.info(create_result)
        except Exception as e:
            _logger.error('插入消息失败:' + str(e))
            print e


    def send_template_message(self,cr,uid,template_code,model_values,openid,wxOfficeAccountInfo,event_entity_id,context):
        env = Environment(cr, uid, context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        text_templates=env['wx.notify_message_template'].search([('template_code','=',template_code),('iseffective','=',True)])
        if len(text_templates)>0:
            text_template=text_templates[0]
            if len(model_values)>1:
                pass
            else:
                template_id = text_template['message_wxtemplate_id']['message_wx_templateid']
                templates_value = text_template['message_wxtemplate_id']['message_templateid']
                url=text_template['message_wxtemplate_id']['message_template_url']
                model=model_values[0]
                association_order=[]
                if 'id' in model['model_value']:
                    association_order.append({
                            "id":model['model_value']['id']
                        })
                postdata = {}
                postdata.update({
                    "touser": openid,
                    "template_id": template_id.replace(' ', ''),
                    "url": self.replacecontent(url,model['model_value'],user,context)
                })
                print model
                tempalte_item = {}
                for i in templates_value:
                    print i
                    value=""
                    if i["template_value"]:
                        value=self.replacecontent(i["template_value"],model['model_value'],user,context)
                    tempalte_item.update({
                        i["template_key"]:
                            {
                                "value": value.decode(),
                                "color": "#173177"
                            }
                    })
                postdata.update({
                    "data": (tempalte_item)
                })
                _logger.info("postdata:" + json.dumps(postdata, ensure_ascii=False))
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component_appid,wxOfficeAccountInfo.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    pass
                else:
                    templateManager = template_manager.template_manager(wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['wx_appsecret'])
                    sendresult = templateManager.send_templdate(postdata)
                    if sendresult['errcode']==0:
                        msgid=sendresult['msgid']
                        postdata.update({
                            'id':model['id']
                        })
                        self.insert_template_record(openid,wxOfficeAccountInfo,env,postdata,text_template,json.dumps(association_order),msgid,event_entity_id)
        else:
            pass
    def insert_template_record(self,openid,wxOfficeAccountInfo,env,messages,mpnews_template,association_order,msgid,event_entity_id=0):
        data = {}
        wx_customer=env['wx.customer'].search([('openid','=',openid)])
        wx_userid=0
        if wx_customer:
            wx_userid=wx_customer[0].id
        else:
            from yuancloud.addons.wx_platform.models import wx_customer as wx_customer
            wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(env.cr, env.uid, env.context)
            values = {}
            values['openid'] = openid
            values['officialaccount_id'] = wxOfficeAccountInfo['wx_id']
            wx_customerinfo = wx_customer_4subscribe.create_wx_customer(values)
            wx_userid=wx_customerinfo.id
        createTime = (int)(time.time())
        print createTime
        value = time.localtime(createTime)
        createtime = time.strftime("%Y-%m-%d %H:%M:%S", value)
        print createtime
        data.update({
            'official_username': wx_userid,
            'message_event': 'send',
            'message_msgid':msgid,
            'model_id':messages['id'],
            'message_status':'sending',
            'createTime': createtime,
            'officialaccount': wxOfficeAccountInfo['id'],
            'message_template':mpnews_template['id'],
            'association_order':association_order,
            'send_event':event_entity_id
            })
        print data
        try:
            create_result = env['wx.notify_message_record'].create(data)
            _logger.info(create_result)
            print create_result
            for message_index in range(0,len(messages['data'].keys())):
                mpnewsinfo={}
                mpnewsinfo.update({
                    "templateid":create_result['id'],
                    "template_key":(messages['data'].keys())[message_index],
                    "template_value":messages['data'][(messages['data'].keys())[message_index]]['value'],
                    "template_remark":""
                })
                print mpnewsinfo
                create_mpnews_result = env['wx.notify_record_value'].create(mpnewsinfo)
        except Exception as e:
            _logger.error('插入图文消息失败:' + str(e))
            print e
