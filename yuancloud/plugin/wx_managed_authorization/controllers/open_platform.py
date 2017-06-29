# -*- coding: utf-8 -*-

from lxml import etree
from yuancloud import SUPERUSER_ID
from yuancloud.addons.wx_base.sdks.openplatform_sdk import WXBizMsgCrypt
from yuancloud.addons.wx_base.sdks.openplatform_sdk import public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
import time
from yuancloud import cache
import logging
from urllib import unquote
from urllib import quote
_logger = logging.getLogger(__name__)
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from yuancloud.api import Environment
from yuancloud import http, api, registry, models
from yuancloud import http
from yuancloud.http import request
from yuancloud.addons.wx_platform.models import wx_customer as customer
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import custom_manager

class open_auth(http.Controller):

    @http.route(['/ycloud_base/authorize_recevice'],type="http", auth='none', csrf=False)
    def recevice_auth(self, **kw):
        env = Environment(request.cr, SUPERUSER_ID, request.context)
        data = http.request.httprequest.url  # web.input()
        print "URL:" + data
        print http.request.httprequest.host
        if http.request.httprequest.method == 'GET':
            return str(1)
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
        data = http.request.httprequest.data
        print data
        xmldata={}
        for el in etree.fromstring(data):
                xmldata[el.tag] = el.text
        appid=xmldata['AppId']
        print "appid"+appid
        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',appid),('auth_component_platfromtype','=','openplatform')])
        auth_component_id=0
        if len(third_platform)==0:
            symmetric_key="essFuyMNenzJptkXq4MjZ6OTjnA4on7vdMaMrDmqy0I"
            appsercret="d4624c36b6795d1d99dcf0547af5443d"
            token="token"
        else:
            auth_component_id=third_platform[0]['id']
            symmetric_key=third_platform[0]['auth_component_encodingasekey']#"essFuyMNenzJptkXq4MjZ6OTjnA4on7vdMaMrDmqy0I"
            appsercret=third_platform[0]['auth_component_appsecret']#"d4624c36b6795d1d99dcf0547af5443d"
            token=third_platform[0]['auth_component_token']#"token"
        redirect_url=http.request.httprequest.host_url+"ycloud_base/authorize_complete/"+appid
        wXBizMsgCrypt=WXBizMsgCrypt.WXBizMsgCrypt(token,symmetric_key,appid)
        decrypt_data=wXBizMsgCrypt.DecryptMsg(data,signature,timestamp,nonce)
        if decrypt_data[0]==0:
            postdata = {}
            for el in etree.fromstring(decrypt_data[1]):
                postdata[el.tag] = el.text
            print postdata
            if 'InfoType' in decrypt_data[1]:
                if postdata['InfoType']=="unauthorized":
                    appId=postdata['AppId']
                    print appId
                    authorizerAppid=postdata['AuthorizerAppid']
                    print authorizerAppid
                    createtime=postdata['CreateTime']
                    print u"公众号:"+authorizerAppid+u"取消授权"
                    print createtime
                    encrypt_data= wXBizMsgCrypt.EncryptMsg('success',nonce)
                    return encrypt_data[1]
                elif postdata['InfoType']=="authorized":
                    appId=postdata['AppId']
                    print appId
                    authorizerAppid=postdata['AuthorizerAppid']
                    createtime=postdata['CreateTime']
                    AuthorizationCode=postdata['AuthorizationCode']
                    publicsdk=public_sdk.public_sdk(appId,appsercret)
                    key=appId+"ticket"
                    ticket=cache.redis.get(key)
                    print u'公众号'+authorizerAppid+"时间"+createtime+",授权码"+AuthorizationCode+",授权成功"
                    authorizer_info=publicsdk.api_get_authorizer_info(authorizerAppid,ticket)
                    print authorizer_info
                    nick_name=authorizer_info['authorizer_info']['nick_name']#微信SDK Demo Special 服务号名称
                    user_name=authorizer_info['authorizer_info']['user_name']#gh_eb5e3a772040　
                    print nick_name
                    print user_name
                    officialaccount=env['wx.officialaccount'].search([('wx_id','=',user_name),('is_auth_officialaccount','=',True)])
                    if len(officialaccount)==0:
                        data={}
                        data.update({
                            'wx_id':user_name,
                            'wx_name':nick_name,
                            'wx_appid': authorizerAppid,
                            'is_auth_officialaccount': True,
                            'auth_component':auth_component_id
                        })
                        print data
                        try:
                            create_result = env['wx.officialaccount'].create(data)
                            _logger.debug(create_result)
                        except Exception as e:
                            _logger.error('创建服务号授权应用出错:' + str(e))
                            print e
                    encrypt_data= wXBizMsgCrypt.EncryptMsg('success',nonce)
                    return encrypt_data[1]
                elif postdata['InfoType']=="updateauthorized":
                    authorizerAppid=postdata['AuthorizerAppid']
                    createtime=postdata['CreateTime']
                    AuthorizationCode=postdata['AuthorizationCode']
                    print u'公众号'+authorizerAppid+"时间"+createtime+",授权码"+AuthorizationCode+",更新授权成功"
                    #return 'success'
                    encrypt_data= wXBizMsgCrypt.EncryptMsg('success',nonce)
                    return encrypt_data[1]
                elif postdata['InfoType']=="component_verify_ticket":
                    ticket=postdata['ComponentVerifyTicket']
                    print ticket
                    key=appid+"ticket"
                    cache.redis.set(key, ticket,600)
                    publicsdk=public_sdk.public_sdk(appid,appsercret)
                    token=publicsdk.get_api_component_token(ticket)
                    print token
                    authcode= publicsdk.get_api_create_preauthcode(ticket)
                    print authcode
                    url="https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid="+appid+"&pre_auth_code="+authcode+"&redirect_uri="+redirect_url
                    print url
                    cache.redis.set("url",url,600)
                    encrypt_data= wXBizMsgCrypt.EncryptMsg('success',nonce)
                    return encrypt_data[1]
            else:
                messageinfo=reply_information.reply_information()
                text= wXBizMsgCrypt.EncryptMsg(messageinfo.text_reply_xml(postdata['FromUserName'],postdata['ToUserName'],int(time.time()),u'test'),nonce)
                return text[1]
        else:
            print decrypt_data[0]

    @http.route('/ycloud_base/authorize_complete/<key>',auth='none',methods=['post','get'])
    def authorize_complete(self,**kw):
        env = Environment(request.cr, SUPERUSER_ID, request.context)
        auth_code=kw['auth_code']
        component_appid=kw['key']
        #component_appid="wx8a79b1dd516ef8d7"
        #component_sercret="d4624c36b6795d1d99dcf0547af5443d"
        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',component_appid),('auth_component_platfromtype','=','openplatform')])
        if len(third_platform)==0:
            component_sercret="d4624c36b6795d1d99dcf0547af5443d"
        else:
            component_sercret=third_platform[0]['auth_component_appsecret']
        key=component_appid+"ticket"
        ticket=cache.redis.get(key)
        publicsdk=public_sdk.public_sdk(component_appid,component_sercret)
        token=publicsdk.api_query_auth(auth_code,ticket)
        print token
        authorizer_appid=token['authorization_info']['authorizer_appid']
        authorizer_access_token=token['authorization_info']['authorizer_access_token']
        authorizer_refresh_token=token['authorization_info']['authorizer_refresh_token']
        cache.redis.set(authorizer_appid+"authorizer_access_token",authorizer_access_token,7200)
        print sys.maxint
        cache.redis.set(authorizer_appid+"authorizer_refresh_token",authorizer_refresh_token,9000000)
        officialaccount=env['wx.officialaccount'].search([('wx_appid','=',authorizer_appid),('is_auth_officialaccount','=',True),('auth_component','=',third_platform[0].id)])
        #更新刷新token
        if officialaccount:
            officialaccount[0]['authorizer_refresh_token']=authorizer_refresh_token
        return 'sucess'

    @http.route('/ycloud_base/message/<key>',auth='none',methods=['post','get'],csrf=False)
    def message(self,**kw):
        env = Environment(request.cr, SUPERUSER_ID, request.context)
        print kw
        appid=kw['key']
        print appid
        data = http.request.httprequest.data
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
        print data
        token = "token"
        officialaccount=env['wx.officialaccount'].search([('wx_id','=',appid),('is_auth_officialaccount','=',True)])
        if not officialaccount:
            symmetric_key="essFuyMNenzJptkXq4MjZ6OTjnA4on7vdMaMrDmqy0I"
            component_appid="wx8a79b1dd516ef8d7"
            component_sercret="d4624c36b6795d1d99dcf0547af5443d"
            token="token"
        else:
            symmetric_key=officialaccount[0]['auth_component']['auth_component_encodingasekey']#"essFuyMNenzJptkXq4MjZ6OTjnA4on7vdMaMrDmqy0I"
            component_appid=officialaccount[0]['auth_component']['auth_component_appid']#"wx8a79b1dd516ef8d7"
            component_sercret=officialaccount[0]['auth_component']['auth_component_appsecret']#d4624c36b6795d1d99dcf0547af5443d
            token = officialaccount[0]['auth_component']['auth_component_token']
        token=unquote(token)
        timestamp=unquote(timestamp)
        msg_signature=unquote(msg_signature)
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,component_appid)
        decrypt_data = wXBizMsgCrypt.DecryptMsg(data, msg_signature, timestamp, nonce)
        print decrypt_data
        postdata={}
        if decrypt_data[0]==0:
            for el in etree.fromstring(decrypt_data[1]):
                postdata[el.tag] = el.text
        msgType=postdata['MsgType']
        fromUser=postdata['FromUserName']
        toUser=postdata['ToUserName']
        if msgType=="event":
            print '事件'
            return self.handler_event(postdata,wXBizMsgCrypt,nonce,request.cr,http.request.context)
        elif msgType=="text":
            msgId = postdata['MsgId']
            key = msgId
            msgvalue = cache.redis.get(key)
            if msgvalue==None:
                cache.redis.set(key, key, 5000)
                content=postdata['Content']
                if content=="TESTCOMPONENT_MSG_TYPE_TEXT":
                    messageinfo=reply_information.reply_information()
                    text=messageinfo.text_reply_xml(postdata['FromUserName'],postdata['ToUserName'],int(time.time()),u'TESTCOMPONENT_MSG_TYPE_TEXT_callback')
                    print text
                    result=  wXBizMsgCrypt.EncryptMsg(text,(nonce))
                    print result
                    return result[1]
                elif content=="测试":
                    messageinfo=reply_information.reply_information()
                    reply_info=u"测试部门"
                    print reply_info
                    text=messageinfo.text_reply_xml(postdata['FromUserName'],postdata['ToUserName'],int(time.time()),reply_info)
                    print text
                    result= wXBizMsgCrypt.EncryptMsg(text.encode('utf-8'),(nonce))
                    print result
                    return result[1]
                threaded_run = threading.Thread(target=self.handler_text,args=(postdata,request.cr,http.request.context,component_appid,appid,component_sercret,wXBizMsgCrypt,nonce))
                threaded_run.start()
                return ""
            else:
                return ""
        elif msgType=="image":
            return self.handler_image(postdata,request.cr,http.request.context)
        elif msgType=="voice":
            return self.handler_voice(postdata,request.cr,http.request.context)
        elif msgType=="video":
            return self.handler_video(postdata,request.cr,http.request.context)
        elif msgType=="link":
            return self.handler_link(postdata,request.cr,http.request.context)
        elif msgType=="LOCATION":
            return self.handler_location(postdata,request.cr,http.request.context)
        elif msgType == "shortvideo":
            return self.handler_shortvideo(postdata, request.cr,http.request.context)
        else:
            messageinfo=reply_information.reply_information()
            return messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),u"默认未实现")

    def handler_event(self,jsonStr,wXBizMsgCrypt,nonce,cr,context):
        eventType=jsonStr['Event']
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
        create_time=jsonStr['CreateTime']
        key=fromUser+create_time
        msgvalue=cache.redis.get(key)
        messageinfo=reply_information.reply_information()
        if msgvalue==None:
            logging.info(u"服务号ID"+toUser)
            cache.redis.set(key, key,5000)
            if eventType=="CLICK":  #点击事件；
                env = Environment(cr, SUPERUSER_ID, http.request.context)
                eventkey=jsonStr['EventKey']
                fromUser=jsonStr['FromUserName']
                toUser=jsonStr['ToUserName']
                if eventkey=="service":
                    env['receive_message'].process_clickkey(eventkey,jsonStr)
                    return env['send_message'].reply_service_message(fromUser, toUser)
                return env['receive_message'].process_clickkey(eventkey,jsonStr)
                #return messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),"Click")
            # elif eventType=="submit_membercard_user_info": #激活会员卡信息
            #     return messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),"submit_membercard_user_info")
            elif eventType == "subscribe":
                env = Environment(cr, SUPERUSER_ID, http.request.context)
                eventKey=jsonStr['EventKey']
                eventKey=eventKey.replace('qrscene_','')
                values={}
                #必须传递的
                values['openid']=fromUser
                values['officialaccount_id']=toUser
                #非必须
                values['subscribe']=True #不传则按False处理（True：关注；False：取消关注）
                values['key']=eventKey  #通过key值查找门店
                wx_customer=env['wx.customer'].search([('openid','=',fromUser)])
                wx_userid=0
                if wx_customer:
                    pass
                else:
                    wx_customer_4subscribe=customer.wx_customer_4subscribe(cr,SUPERUSER_ID,http.request.context)
                    wx_customer_4subscribe.create_wx_customer(values)
                cr.commit()
                return env['receive_message'].process_clickkey("default",jsonStr)
            elif eventType=="card_merchant_auth_check_result":
                SubMerchantAppId=jsonStr['SubMerchantAppId']
                IsPass=jsonStr['IsPass']
                Reason=jsonStr['Reason']
                result=""
                if IsPass:
                    result="子商户:"+SubMerchantAppId+"审核通过"
                else:
                    result="子商户:"+SubMerchantAppId+"审核失败，原因为:"+Reason
                text= messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),result)
                text=wXBizMsgCrypt.EncryptMsg(text,nonce)
                return text[1]
            else:
                content=eventType+"from_callback"
                result= messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),content)
                text= wXBizMsgCrypt.EncryptMsg(result,nonce)
                print text
                return text[1]
        else:
            return  messageinfo.text_reply_xml(fromUser,toUser,int(time.time()),"")

    def handler_text(self,jsonStr,cr,context,component_appid,appid,component_sercret,wXBizMsgCrypt,nonce):
        dbname = cr.dbname
        uid = SUPERUSER_ID
        context = context.copy()
        #component_sercret="d4624c36b6795d1d99dcf0547af5443d"
        with api.Environment.manage():
            with registry(dbname).cursor() as new_cr:
                env = Environment(new_cr, uid, context)
                content=unquote(jsonStr['Content'].decode('utf-8'))
                print content
                if content.startswith('QUERY_AUTH_CODE'):
                    query_auth_code=content.replace('QUERY_AUTH_CODE:','')
                    key=component_appid+"ticket"
                    ticket=cache.redis.get(key)
                    publicsdk=public_sdk.public_sdk(component_appid,component_sercret)
                    token=publicsdk.api_query_auth(query_auth_code,ticket)
                    reply_content=query_auth_code+"_from_api"
                    custom_manager.sendText_custommessage_access_token(jsonStr['FromUserName'],reply_content,"",token['authorization_info']['authorizer_access_token'])
                    return
                key=component_appid+"ticket"
                ticket=cache.redis.get(key)
                publicsdk=public_sdk.public_sdk(component_appid,component_sercret)
                refresh_token_key=appid+"authorizer_refresh_token"
                refresh_token=cache.redis.get(refresh_token_key)
                api_authorizer_token=publicsdk.api_authorizer_token(ticket,appid,refresh_token)
                print "api_authorizer_token:"+str(api_authorizer_token)
                #custom_manager.sendText_custommessage_access_token(jsonStr['FromUserName'],"测试","",api_authorizer_token)
                return  env['receive_message'].accept_message('wx.message_text',jsonStr)

    def handler_image(self,jsonStr,cr,uid):
        messageinfo=reply_information.reply_information()
        imageId=jsonStr["MediaId"]
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            # env['ycloud.wx.message'].create_message('ycloud.wx.message_image', jsonStr)
            env['receive_message'].accept_message('wx.image_message_record', jsonStr)
            return ""
        return ""

    def handler_voice(self,jsonStr,cr,uid):
        messageinfo=reply_information.reply_information()
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
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

    def handler_video(self,jsonStr,cr,uid):
        messageinfo=reply_information.reply_information()
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
        videoId=jsonStr["MediaId"]
        title=jsonStr["Title"]
        description=jsonStr["Description"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.video_message_record', jsonStr)
            return ""
        else:
            return ""

    def handler_link(self,jsonStr,cr,uid):
        messageinfo=reply_information.reply_information()
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
        linktitle=jsonStr["Title"]
        linkdescription=jsonStr["Description"]
        linkurl=jsonStr["Url"]
        env = Environment(cr, uid, http.request.context)
        key = jsonStr['MsgId']
        msgvalue = cache.redis.get(key)
        if msgvalue == None:
            cache.redis.set(key, key, 1000)
            env['receive_message'].accept_message('wx.link_message_record', jsonStr)
            return ""
        return ""
    def handler_location(self,jsonStr,cr,uid):
        messageinfo=reply_information.reply_information()
        fromUser=jsonStr['FromUserName']
        toUser=jsonStr['ToUserName']
        locationX=jsonStr["Location_X"]
        locationY=jsonStr["Location_Y"]
        scale=jsonStr["Scale"]
        label=jsonStr["Label"]
        key = jsonStr['MsgId']
        locationInfo=u"你发送的是位置，纬度为："+locationX+u"；经度为："+locationY+u"；缩放级别为："+scale+u"；位置为："+label;
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





