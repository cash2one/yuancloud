# -*- coding: utf-8 -*-
from lxml import etree
import urllib2
import logging
import time

try:
    import simplejson as json
except ImportError:
    import json
import base64
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import card_manager
from yuancloud.addons.wx_platform.models import wx_customer as customer
from yuancloud import http
from yuancloud.api import Environment
from yuancloud import cache
from yuancloud.addons.wx_base.sdks.openplatform_sdk import WXBizMsgCrypt
import os
import threading
from yuancloud import http, api, registry, models

_logger = logging.getLogger(__name__)
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class wx_index:
    def check_server_valid(self, request, cfg_apppartner):
        # 获取输入参数
        data = request.url  # web.input()
        print "URL:" + data
        timestamp = ""
        signature = ""
        nonce = ""
        echostr = ""
        result = data.split('?')[-1]
        for key_value in result.split('&'):
            keyvalues = key_value.split('=')
            if keyvalues[0] == "signature":
                signature = keyvalues[1]
            elif keyvalues[0] == "timestamp":
                timestamp = keyvalues[1]
            elif keyvalues[0] == "nonce":
                nonce = keyvalues[1]
            elif keyvalues[0] == "echostr":
                echostr = keyvalues[1]
        # 自己的token
        token = cfg_apppartner['officalaccount']['wx_apptoken']  # 这里改写你在微信公众平台里输入的token
        print "token:" + token
        print "timestamp:" + timestamp
        print "nonce:" + nonce
        print "signature:" + signature
        # 字典序排序
        list = [token, timestamp, nonce]
        list.sort()
        import hashlib
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        # sha1加密算法
        # 如果是来自微信的请求，则回复echostr
        print "hashcode:" + hashcode
        if hashcode == signature:
            print "相等"
            return echostr
        else:
            print "不相等"
            return "1"

    # 分析微信数据并进行处理

    def execute_wx(self, cr, uid, data, cfg_apppartner):
        postdata = {}
        for el in etree.fromstring(data):
            postdata[el.tag] = el.text
        print http.request.httprequest.url
        print postdata
        is_encrypt = False
        msg_signature = ""
        timestamp = ""
        nonce = ""
        _logger.debug(json.dumps(postdata))
        if 'encrypt_type' in http.request.httprequest.url:
            result = http.request.httprequest.url.split('?')[-1]
            encrypt_type = ""
            for key_value in result.split('&'):
                keyvalues = key_value.split('=')
                if keyvalues[0] == "encrypt_type":
                    encrypt_type = keyvalues[1]
                elif keyvalues[0] == "msg_signature":
                    msg_signature = keyvalues[1]
                elif keyvalues[0] == "timestamp":
                    timestamp = keyvalues[1]
                elif keyvalues[0] == "nonce":
                    nonce = keyvalues[1]
                elif keyvalues[0] == "echostr":
                    echostr = keyvalues[1]
            if encrypt_type == "aes":
                env = Environment(cr, uid, http.request.context)
                is_encrypt = True
                token = cfg_apppartner['officalaccount']['wx_apptoken']
                symmetric_key = cfg_apppartner['officalaccount'][
                    'wx_encodingasekey']
                wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,
                                                            cfg_apppartner['officalaccount']['wx_appid'])
                decrypt_data = wXBizMsgCrypt.DecryptMsg(data, msg_signature, timestamp, nonce)
                print decrypt_data
                if decrypt_data[0] == 0:
                    for el in etree.fromstring(decrypt_data[1]):
                        postdata[el.tag] = el.text
                else:
                    errcode = str(decrypt_data[0])
                    messageinfo = reply_information.reply_information()
                    messageinfo.text_reply_xml("", postdata['ToUserName'], int(time.time()), errcode)
                    encrypt_data = wXBizMsgCrypt.EncryptMsg(errcode, nonce)
                    print encrypt_data[1]
                    return encrypt_data[1]
        msgType = postdata['MsgType']
        fromUser = postdata['FromUserName']
        toUser = postdata['ToUserName']
        if msgType == "event":
            return self.handler_event(postdata, cr, uid)
        elif msgType == "text":
            return self.handler_text(postdata, cr, uid)
        elif msgType == "image":
            return self.handler_image(postdata, cr, uid)
        elif msgType == "voice":
            return self.handler_voice(postdata, cr, uid)
        elif msgType == "video":
            return self.handler_video(postdata, cr, uid)
        elif msgType == "link":
            return self.handler_link(postdata, cr, uid)
        elif msgType == "location":
            return self.handler_location(postdata, cr, uid)
        elif msgType == "shortvideo":
            return self.handler_shortvideo(postdata, cr, uid)
        else:
            messageinfo = reply_information.reply_information()
            return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), u"默认未实现")

    def userisadd(self, openid):
        return True

    def handler_event(self, jsonStr, cr, uid):
        eventType = jsonStr['Event']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        create_time = jsonStr['CreateTime']
        key = fromUser + create_time
        # mc=wx_public_sdk.getClient()
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        if msgvalue == None:
            logging.debug(u"服务号ID" + toUser)
            env = Environment(cr, uid, http.request.context)
            wxOfficeAccountInfo = env['wx.officialaccount'].getofficialaccount(toUser)
            # print "appid:" + wxOfficeAccountInfo["wx_appid"]
            # print "appsecret" + wxOfficeAccountInfo["wx_appsecret"]
            cache.redis.set(key, key, 50000)
            # mc.set(key,key,50)
            if eventType == "CLICK":  # 点击事件；
                context=http.request.context
                context.update({
                    "openid":fromUser
                })
                env = Environment(cr, uid, context)
                eventkey=jsonStr['EventKey']
                fromUser=jsonStr['FromUserName']
                toUser=jsonStr['ToUserName']
                if eventkey=="service":
                    env['receive_message'].process_clickkey(eventkey,jsonStr)
                    return env['send_message'].reply_service_message(fromUser, toUser)
                return env['receive_message'].process_clickkey(eventkey,jsonStr)
            # elif eventType == "submit_membercard_user_info":  # 激活会员卡信息
            #     submitcard = ycloud_wx_submitusercard.ycloud_wx_submit_card_userinfo()
            #     return submitcard.submit_membercard_user_info(cr, uid, jsonStr, wxOfficeAccountInfo)
            elif eventType == "subscribe":
                eventKey=jsonStr['EventKey']
                eventKey=eventKey.replace('qrscene_','')
                values={}
                #必须传递的
                values['openid']=fromUser
                values['officialaccount_id']=toUser
                #非必须
                values['subscribe']=True #不传则按False处理（True：关注；False：取消关注）
                values['key']=eventKey  #通过key值查找门店
                #values['subscribe_time']='2015-12-22 20:35:20' #不传则按当前时间处理
                # scanvalues={}
                # scanvalues['scene']="subscribe"
                # if eventKey=="":
                #     values['subscribe_source']='manual' #（scan扫码关注；manual：手工关注)
                # else:
                #     values['subscribe_source']='scan'
                # scanvalues['scancode_key']=eventKey
                # env = Environment(cr, uid, http.request.context)
                # qr_management = env['ycloud.qr.management'].search(
                # ['|', ('scene_str', '=', eventKey), ('scene_id', '=', int(eventKey) if eventKey.isdigit() else -1)])
                # qr_models_values=[]
                # qr_key=""
                # if len(qr_management) > 0:
                #     scanvalues['scene']=qr_management[0]['qr_scene']
                #     qr_key=qr_management[0]['qr_key']
                # else:
                #     qr_key=eventKey
                # scanvalues['openid']=fromUser
                # scanvalues['officialaccount_appid']=wxOfficeAccountInfo['wx_appid']
                wx_customer=env['wx.customer'].search([('openid','=',fromUser)])
                wx_userid=0
                if wx_customer:
                    pass
                else:
                    wx_customer_4subscribe=customer.wx_customer_4subscribe(cr,uid,http.request.context)
                    wx_customer_4subscribe.create_wx_customer(values)
                cr.commit()
                # def create_wx_customer(qr_key,eventKey,scanvalues,cr,uid,context,fromUser,toUser,wxOfficeAccountInfo):
                #     dbname = cr.dbname
                #     uid = uid
                #     context = context.copy()
                #     with api.Environment.manage():
                #         with registry(dbname).cursor() as new_cr:
                #             context.update({
                #                     "openid":fromUser
                #                 })
                #             new_env = Environment(new_cr, uid, context)
                #             qr_management = new_env['ycloud.qr.management'].search(['|', ('scene_str', '=', eventKey), ('scene_id', '=', int(eventKey) if eventKey.isdigit() else -1)])
                #             qr_models_values=[]
                #             if len(qr_management) > 0:
                #                 qr_models = qr_management[0]['qr_models']
                #                 for qr_model in qr_models:
                #                     model_info=qr_model['model_id']['model']
                #                     model_id_value=qr_model['model_id_value']
                #                     model_column=qr_model['model_column']['name']
                #                     orderinfo=new_env[model_info].search([(model_column,'=',model_id_value)])[0]
                #                     value={}
                #                     value.update({
                #                         'id':qr_model['model_id']['id'],
                #                         'model_value':orderinfo
                #                     })
                #                     qr_models_values.append(value)
                #             if qr_key<>"":
                #                 if len(qr_models_values)==0:
                #                     _logger.info("无参考模型数据")
                #                     new_env['receive_message'].process_clickkey(qr_key,jsonStr)
                #                 else:
                #                     _logger.info("有参考模型数据")
                #                     new_env['ycloud.wx.message.send_event'].sendmessage_TriggeredbyCommand(qr_key,qr_models_values)
                #                 scancode_help=scancode.scancode(new_cr,uid,context)
                #                 scancode_help.create_scancode(scanvalues)
                # threaded_run = threading.Thread(target=create_wx_customer,args=(qr_key,eventKey,scanvalues,cr,uid,http.request.context,fromUser,toUser,wxOfficeAccountInfo))
                # threaded_run.start()
                return env['receive_message'].process_clickkey("default",jsonStr)
            # elif eventType == "WifiConnected":  # WIFI链接成功
            #     mac = jsonStr['DeviceNo']#联网设备MAC
            #     shop_id = jsonStr['ShopId']
            #     connectTime = jsonStr['ConnectTime']
            #     message = "用户:" + fromUser + "在门店ID:" + shop_id + "时间" + connectTime + "连网成功"
            #     opendid=jsonStr['FromUserName']
            #     _logger.info("WIFI:"+message)
            #     if self.userisadd(opendid):
            #         #找到MAC对应的门店负责人:
            #         qr=env['ycloud.qr.management'].search([('qr_mac','=',mac)])
            #         print qr
            #         if qr:
            #             store_open_id=qr[0]['o2o_store']['store_owner']['oauth_open_id']
            #             print store_open_id
            #             if store_open_id:
            #                 eventKey="wifiConnected"
            #                 jsonStr.update({
            #                     'FromUserName':store_open_id
            #                 })
            #                 env['receive_message'].process_clickkey(eventKey,jsonStr)
            #         pass
            #     return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")
            # elif eventType == "card_pass_check":  # 会员卡审核通过
            #     cardid = jsonStr['CardId']
            #     try:
            #         env = Environment(cr, uid, http.request.context)
            #         env['ycloud.wx.membership.line'].modify_wx_membership_line(cardid, 1)
            #     except Exception as e:
            #         _logger.error(e)
            #     return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")
            # elif eventType == "card_not_pass_check":  # 会员卡审核失败
            #     cardid = jsonStr['CardId']
            #     try:
            #         env = Environment(cr, uid, http.request.context)
            #         env['ycloud.wx.membership.line'].modify_wx_membership_line(cardid, 0)
            #     except Exception as e:
            #         _logger.error(e)
            #     return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")
            # elif eventType == "user_get_card":  # 用户领用卡劵时；
            #     CardId = jsonStr["CardId"]
            #     UserCardCode = jsonStr["UserCardCode"]
            #     data = {}
            #     data["openid"] = fromUser
            #     data["officialaccount"] = wxOfficeAccountInfo['wx_official_account_id']
            #     data['cardid'] = CardId
            #     data['cardcode'] = UserCardCode
            #     try:
            #         env = Environment(cr, uid, http.request.context)
            #         create_result = env['ycloud.wx.membership'].create_wx_membership(data)
            #     except Exception as e:
            #         _logger.debug("创建会员卡记录失败:" + str(e))
            #         print e
            #     return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")
            elif eventType == "TEMPLATESENDJOBFINISH":
                time.sleep(10)
                MsgID = jsonStr['MsgID']
                Status = jsonStr['Status']
                messageStatus = ""
                if Status == "success":
                    messageStatus = "use_sucess"
                elif Status == "failed:user block":
                    messageStatus = "use_block"
                elif Status == "failed: system failed":
                    messageStatus = "system_fail"
                try:
                    cr.commit()
                    env = Environment(cr, uid, http.request.context)
                    messages = env['wx.notify_message_record'].search([('message_msgid', '=', MsgID)])
                    data = {}
                    data.update({
                        'message_status': messageStatus
                    })
                    print data
                    messages[0].write(data)
                except Exception as e:
                    _logger.debug("更新消息状态失败:" + str(e))
                    print e
                return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")
            elif eventType == "SCAN":
                eventKey = jsonStr['EventKey']
                print eventKey
                def scanbarcode(eventKey,cr,uid,context,fromUser,wxOfficeAccountInfo):
                    dbname = cr.dbname
                    uid = uid
                    context = context.copy()
                    with api.Environment.manage():
                        with registry(dbname).cursor() as new_cr:
                            context.update({
                            "openid":fromUser
                            })
                            new_env = Environment(new_cr, uid, context)
                            # scanvalues={}
                            # scanvalues['scene']="subscribe"
                            # scanvalues['scancode_key']=eventKey
                            # qr_management = new_env['ycloud.qr.management'].search(['|', ('scene_str', '=', eventKey), ('scene_id', '=', int(eventKey) if eventKey.isdigit() else -1)])
                            # if len(qr_management) > 0:
                            #     scanvalues['scene']=qr_management[0]['qr_scene']
                            #     print scanvalues['scene']
                            # scanvalues['openid']=fromUser
                            # scanvalues['officialaccount_appid']=wxOfficeAccountInfo['wx_appid']
                            # scancode_help=scancode.scancode(new_cr,uid,context)
                            # scancode_help.create_scancode(scanvalues)
                            # qr_key=qr_management[0]['qr_key']
                            # qr_models = qr_management[0]['qr_models']
                            qr_key=eventKey
                            qr_models_values=[]
                            # for qr_model in qr_models:
                            #     model_info=qr_model['model_id']['model']
                            #     model_id_value=qr_model['model_id_value']
                            #     model_column=qr_model['model_column']['name']
                            #     orderinfo=new_env[model_info].search([(model_column,'=',model_id_value)])[0]
                            #     value={}
                            #     value.update({
                            #         'id':qr_model['model_id']['id'],
                            #         'model_value':orderinfo
                            #     })
                            #     qr_models_values.append(value)
                            #currentContext={}
                            if len(qr_models_values)==0:
                                new_env['receive_message'].process_clickkey(qr_key,jsonStr)
                            else:
                                new_env['wx.message.send_event'].sendmessage_TriggeredbyCommand(qr_key,qr_models_values)
                threaded_run = threading.Thread(target=scanbarcode,args=(eventKey,cr,uid,http.request.context,fromUser,wxOfficeAccountInfo))
                threaded_run.start()
                return ""
            # elif eventType=="user_pay_from_pay_cell":#用户使用会员卡买单功能
            #     CardId=jsonStr['CardId']
            #     UserCardCode=jsonStr['UserCardCode']
            #     TransId=jsonStr['TransId']
            #     LocationId=""
            #     if 'LocationId' in jsonStr:
            #         LocationId=jsonStr['LocationId']
            #     LocationName=""
            #     if 'LocationName' in jsonStr:
            #         LocationName=jsonStr['LocationName']
            #     Fee=jsonStr['Fee']
            #     OriginalFee=jsonStr['OriginalFee']
            #     add_bonus=((int)(Fee)*100)
            #     record_bonus="消费"+Fee+"元,获得"+str(add_bonus)+"积分"
            #     add_balance=0
            #     record_balance=0
            #     message = "用户:" + fromUser + "在门店ID:" + LocationId + ",门店名称:" + LocationName + "使用卡劵"+UserCardCode+",实付金额:"+Fee
            #     print message
            #     cardManager = card_manager.card_manager(wxOfficeAccountInfo['wx_appid'],
            #                                         wxOfficeAccountInfo['wx_appsecret'])
            #     cardManager.update_member_card_bonus_info(UserCardCode,CardId,add_bonus,record_bonus,add_balance,record_balance)
            #     return ""
            elif eventType=="unsubscribe":
                wx_customer_4subscribe=customer.wx_customer_4subscribe(cr,uid,http.request.context)
                values={}
                #必须传递的
                values['openid']=fromUser
                values['officialaccount_id']=toUser
                #非必须
                values['subscribe']=False #不传则按False处理（True：关注；False：取消关注）
                wx_customer_4subscribe.create_wx_customer(values)
                return ""
            # elif eventType == "merchant_order":
            #     OrderId = jsonStr['OrderId']
            #     ProductId = jsonStr['ProductId']
            #     try:
            #         context=http.request.context
            #         openid = jsonStr['FromUserName']
            #             #currentContext={}
            #         context.update({
            #             "openid":openid
            #             })
            #         env = Environment(cr, uid, context)
            #         oe_order = env['ycloud.wx.syncrecord'].create_record(OrderId, ProductId, wxOfficeAccountInfo)
            #         if oe_order <> False:
            #             print oe_order['name']
            #             message_key = "merchant_order"
            #             model_instances=[]
            #             model_instance={}
            #             model = env['ir.model'].search([('model', '=', 'sale.order')])[0]
            #             model_instance.update({
            #                     "id":model['id'],
            #                     "model_value":oe_order
            #             })
            #
            #             model_instances.append(model_instance)
            #             env['ycloud.wx.message.send_event'].sendmessage_TriggeredbyCommand(message_key,model_instances)
            #     except Exception as e:
            #         _logger.debug("小店下单事件出错:" + str(e))
            #         print e
            #     return ""
            else:
                return ""
        else:
            return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")

    def handler_text(self, jsonStr, cr, uid):
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        create_time = jsonStr['CreateTime']
        msgId = jsonStr['MsgId']
        key = msgId
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        if msgvalue == None:
            _logger.debug(u"服务号ID" + toUser)
            context = http.request.context
            context.update({
                "openid": fromUser
            })
            env = Environment(cr, uid, context)
            cache.redis.set(key, key, 5000)
            return env['receive_message'].accept_message('wx.message_text', jsonStr)
        else:
            return ""
            # return messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), "")

    def handler_image(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        imageId = jsonStr["MediaId"]
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        msgid = jsonStr['MsgId']
        picurl = jsonStr['PicUrl']
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            # env['ycloud.wx.message'].create_message('ycloud.wx.message_image', jsonStr)
            env['receive_message'].accept_message('wx.image_message_record', jsonStr)
            return ""
        return ""

    def handler_voice(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        recognitionInfo = ""
        if 'Recognition' in jsonStr:
            recognitionInfo = jsonStr["Recognition"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.voice_message_record', jsonStr)
            return ""
        return ""

    def handler_video(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        videoId = jsonStr["MediaId"]
        title = jsonStr["Title"]
        description = jsonStr["Description"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.video_message_record', jsonStr)
            return ""
        else:
            return ""

    def handler_link(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        linktitle = jsonStr["Title"]
        linkdescription = jsonStr["Description"]
        linkurl = jsonStr["Url"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.link_message_record', jsonStr)
            return ""
        return ""

    def handler_location(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        locationX = jsonStr["Location_X"]
        locationY = jsonStr["Location_Y"]
        scale = jsonStr["Scale"]
        label = jsonStr["Label"]
        key = jsonStr['MsgId']
        locationInfo = u"你发送的是位置，纬度为：" + locationX + u"；经度为：" + locationY + u"；缩放级别为：" + scale + u"；位置为：" + label;
        env = Environment(cr, uid, http.request.context)
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.location_message_record', jsonStr)
            return ""
        return ""

    def handler_shortvideo(self, jsonStr, cr, uid):
        messageinfo = reply_information.reply_information()
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        thumbMediaId = jsonStr["ThumbMediaId"]
        mediaId = jsonStr["MediaId"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.video_message_record', jsonStr)
            return ""
        return ""