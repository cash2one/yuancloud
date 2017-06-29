# -*- coding: utf-8 -*-
from yuancloud import http
from lxml import etree
from yuancloud import SUPERUSER_ID
from yuancloud.addons.wx_base.sdks.openplatform_sdk import WXBizMsgCrypt
from yuancloud.addons.wx_base.sdks.openplatform_sdk import public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
import time
from yuancloud import http
from yuancloud.http import request
#from yuancloud.addons.website.models.website import slug
import werkzeug
from yuancloud import cache
import logging
from urllib import unquote
from urllib import  quote
#from yuancloud.addons.ycloud_wx.sdk import user_manager

_logger = logging.getLogger(__name__)

import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from yuancloud.api import Environment

from yuancloud import http, api, registry, models


class qy_main_index:

    # 分析微信数据并进行处理
    def execute_wx_qy(self, cr, uid, data,cfg_apppartner):
        print data
        print cfg_apppartner
        result = http.request.httprequest.url.split('?')[-1]
        msg_signature = ""
        timestamp=""
        nonce=""
        postdata={}
        for key_value in result.split('&'):
            keyvalues = key_value.split('=')
            if keyvalues[0] == "msg_signature":
                msg_signature = keyvalues[1]
            elif keyvalues[0] == "timestamp":
                timestamp = keyvalues[1]
            elif keyvalues[0] == "nonce":
                nonce = keyvalues[1]
            elif keyvalues[0] == "echostr":
                echostr = keyvalues[1]
        token = cfg_apppartner['enterpriseaccount']['wx_apptoken']
        symmetric_key = cfg_apppartner['enterpriseaccount']['wx_encodingasekey']
        appid=cfg_apppartner['enterpriseaccount']['wx_appid']
        token=unquote(token)
        timestamp=unquote(timestamp)
        msg_signature=unquote(msg_signature)
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,appid)
        decrypt_data = wXBizMsgCrypt.DecryptMsg(data, msg_signature, timestamp, nonce)
        if decrypt_data[0] == 0:
            for el in etree.fromstring(decrypt_data[1]):
                postdata[el.tag] = el.text
            print postdata
            msgType = postdata['MsgType']
            fromUser = postdata['FromUserName']
            toUser = postdata['ToUserName']
            result=""
            if msgType == "event":
                result= self.handler_event(postdata, cr, uid)
            elif msgType == "text":
                result= self.handler_text(postdata, cr, uid,wXBizMsgCrypt)
            elif msgType == "image":
                result= self.handler_image(postdata, cr, uid)
            elif msgType == "voice":
                result= self.handler_voice(postdata, cr, uid)
            elif msgType == "video":
                result= self.handler_video(postdata, cr, uid)
            elif msgType == "link":
                result= self.handler_link(postdata, cr, uid)
            elif msgType == "location":
                result= self.handler_location(postdata, cr, uid)
            elif msgType == "shortvideo":
                result= self.handler_shortvideo(postdata, cr, uid)
            else:
                messageinfo = reply_information.reply_information()
                content=u"默认未实现"
                result= messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), content)
            result= wXBizMsgCrypt.EncryptMsg(result.encode('utf-8'),(nonce))
            print result
            return result[1]
        else:
            errcode = str(decrypt_data[0])
            encrypt_data = wXBizMsgCrypt.EncryptMsg(errcode, nonce)
            print encrypt_data[1]
            return encrypt_data[1]
        pass

    def check_server_valid(self,request,cfg_apppartner):
        postdata = {}
        data = request.url  # web.input()
        print "URL:" + data
        timestamp = ""
        signature = ""
        nonce = ""
        echostr = ""
        result = data.split('?')[-1]
        for key_value in result.split('&'):
            keyvalues = key_value.split('=')
            if keyvalues[0] == "msg_signature":
                signature = keyvalues[1]
            elif keyvalues[0] == "timestamp":
                timestamp = keyvalues[1]
            elif keyvalues[0] == "nonce":
                nonce = keyvalues[1]
            elif keyvalues[0] == "echostr":
                echostr = keyvalues[1]
        # 自己的token
        token = cfg_apppartner['enterpriseaccount']['wx_apptoken']
        symmetric_key = cfg_apppartner['enterpriseaccount']['wx_encodingasekey']
        appid=cfg_apppartner['enterpriseaccount']['wx_appid'] # 这里改写你在微信公众平台里输入的token
        token=unquote(token)
        timestamp=unquote(timestamp)
        echostr=unquote(echostr)
        signature=unquote(signature)
        print "token:" + token
        print "timestamp:" + timestamp
        print "nonce:" + nonce
        print "msg_signature:" + signature
        print 'echostr:'+echostr
        #symmetric_key = cfg_apppartner['encodingAESKey']#"N2UAlci4D2WX3xyf6mWdsdCv2T3tIDB4wdNxlDVhuon"
        #appid=cfg_apppartner['appid']#"wxe28ca91a338a7638"
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,
                                                            appid)
        decrypt_data = wXBizMsgCrypt.VerifyURL(signature, timestamp, nonce, echostr)
        print decrypt_data
        if decrypt_data[0] == 0:
            sReplyEchoStr= decrypt_data[1]
            print sReplyEchoStr
            return sReplyEchoStr
        else:
            errcode = str(decrypt_data[0])
            print errcode
        pass

    def handler_event(self,jsonStr, cr, uid):
        #content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        #AgentID=jsonStr['AgentID']
        eventType=jsonStr['Event']
        create_time = jsonStr['CreateTime']
        key = fromUser + create_time
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        if msgvalue == None:
            logging.info(u"服务号ID"+toUser)
            cache.redis.set(key, key,5000)
            if eventType=="click":  #点击事件；
                eventkey=jsonStr['EventKey']
                fromUser=jsonStr['FromUserName']
                toUser=jsonStr['ToUserName']
                return env['receive_message'].process_clickkey(eventkey,jsonStr)
                #return messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),"Click")
            # elif eventType=="submit_membercard_user_info": #激活会员卡信息
            #     return messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),"submit_membercard_user_info")
            elif eventType == "subscribe":
                return env['receive_message'].process_clickkey("default",jsonStr)
        else:
            return ""
        pass

    def handler_text(self, jsonStr,cr, uid,wXBizMsgCrypt):
        content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        AgentID=jsonStr['AgentID']
        msgId = jsonStr['MsgId']
        key = msgId
        # mc=wx_public_sdk.getClient()
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        if msgvalue == None:
            cache.redis.set(key, key, 5000)
            print content
            env = Environment(cr, uid, http.request.context)
            # content=u"测试中心，测试教师"
            # result= messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), content)
            # return result
            return env['receive_message'].accept_qy_message('wx.message_text',jsonStr,AgentID)
        else:
            return ""

    def handler_image(self,postdata, cr, uid):
        pass

    def handler_voice(self,postdata, cr, uid):
        pass

    def handler_video(self,postdata, cr, uid):
        pass

    def handler_link(self,postdata, cr, uid):
        pass

    def handler_location(self,postdata, cr, uid):
        pass

    def handler_shortvideo(self,postdata, cr, uid):
        pass


