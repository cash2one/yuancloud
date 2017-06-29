# -*- coding: utf-8 -*-

from lxml import etree
from yuancloud import SUPERUSER_ID
from yuancloud.addons.wx_base.sdks.openplatform_sdk import WXBizMsgCrypt
from yuancloud.addons.wx_base.sdks.openplatform_sdk import qy_open_public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import reply_information
import time
import xmltodict
from yuancloud.http import request
import werkzeug
from yuancloud import cache
import logging
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
_logger = logging.getLogger(__name__)

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from yuancloud.api import Environment

try:
    import simplejson as json
except ImportError:
    import json
from yuancloud import http, api, registry, models
import os
import sys
import jinja2

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('yuancloud.addons.wx_managed_authorization', "views")

env_jinjia = jinja2.Environment(loader=loader, autoescape=True)
env_jinjia.filters["json"] = json.dumps

class open_qy_auth(http.Controller):

    @http.route('/ycloud_base/access_qy', auth='none', methods=['post', 'get'],csrf=False)
    def access_qy_auth(self, **kw):
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
        # appid=""
        data = http.request.httprequest.data
        print data
        xmldata = {}
        for el in etree.fromstring(data):
            xmldata[el.tag] = el.text
        appid = xmldata['ToUserName']
        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',appid),('auth_component_platfromtype','!=','openplatform')])
        if len(third_platform)==0:
            symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
            appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
            token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
            if appid == 'tjeaae807dcefd96c8':
                appsercret = "lok8-TQ1d3n1pUZW86nKiG-b3DUYHdAwGwnDPQj23U15I_iOxHhOi5HATn8GJvem"
            elif appid=="tj0072de65cebdab77":
                appsercret="SoJ4APxNnhpSlqcQ5u-lpnE_fUP0t2t_XfbMMr_eL-kEl-1v0sDfhn4kkdBDBF0D"
        else:
            symmetric_key=third_platform[0]['auth_component_encodingasekey']
            appsercret=third_platform[0]['auth_component_appsecret']
            token=third_platform[0]['auth_component_token']
        # symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
        #
        # appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
        # token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
        #
        # if appid == 'tjeaae807dcefd96c8':
        #     appsercret = "lok8-TQ1d3n1pUZW86nKiG-b3DUYHdAwGwnDPQj23U15I_iOxHhOi5HATn8GJvem"
        # elif appid=="tj0072de65cebdab77":
        #     appsercret="SoJ4APxNnhpSlqcQ5u-lpnE_fUP0t2t_XfbMMr_eL-kEl-1v0sDfhn4kkdBDBF0D"
        # print "appid"+appid
        redirect_url = http.request.httprequest.host_url + "ycloud_base/qy_auth/" + appid
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key, appid)
        decrypt_data = wXBizMsgCrypt.DecryptMsg(data, signature, timestamp, nonce)
        if decrypt_data[0] == 0:
            postdata = {}
            for el in etree.fromstring(decrypt_data[1]):
                postdata[el.tag] = el.text
            print postdata
            if 'InfoType' in decrypt_data[1]:
                if postdata['InfoType'] == "cancel_auth":
                    appId = postdata['SuiteId']
                    print appId
                    authorizerAppid = postdata['AuthCorpId']
                    print authorizerAppid
                    createtime = postdata['TimeStamp']
                    print u"企业号:" + authorizerAppid + u"取消授权"
                    print createtime
                    # return 'sucess'
                    encrypt_data = wXBizMsgCrypt.EncryptMsg('success', nonce)
                    return encrypt_data[1]
                elif postdata['InfoType'] == "change_auth":
                    authorizerAppid = postdata['AuthCorpId']
                    createtime = postdata['TimeStamp']
                    SuiteId = postdata['SuiteId']
                    print u'企业号号' + authorizerAppid + "时间" + createtime + ",在套件" + SuiteId + ",变更授权"
                    # return 'success'
                    encrypt_data = wXBizMsgCrypt.EncryptMsg('success', nonce)
                    return encrypt_data[1]
                elif postdata['InfoType'] == "suite_ticket":
                    ticket = postdata['SuiteTicket']
                    SuiteId = postdata['SuiteId']
                    print ticket
                    key = appid + "ticket"
                    print appid
                    cache.redis.set(key, ticket, 600)
                    suite_access_token = qy_open_public_sdk.get_suite_token(SuiteId, appsercret, ticket)
                    pre_auth_code = qy_open_public_sdk.get_pre_auth_code(SuiteId, suite_access_token)
                    print pre_auth_code
                    baseurl = "https://qy.weixin.qq.com/cgi-bin/loginpage?suite_id=" + SuiteId + "&pre_auth_code=" + pre_auth_code + "&redirect_uri=" + redirect_url + "&state=state"
                    print baseurl
                    timestamp = int(time.time())
                    redirect_login_url = http.request.httprequest.host_url + "ycloud_base/auth_login"
                    authurl = "https://qy.weixin.qq.com/cgi-bin/loginpage?corp_id="+appid+"&redirect_uri=" + redirect_login_url + "&state=" + str(timestamp) + "&usertype=admin"
                    cache.redis.set("baseurl" + SuiteId, baseurl, 600)
                    cache.redis.set('authurl', authurl, 600)
                    encrypt_data = wXBizMsgCrypt.EncryptMsg('success', nonce)
                    return encrypt_data[1]
            else:
                messageinfo = reply_information.reply_information()
                text = wXBizMsgCrypt.EncryptMsg(
                    messageinfo.text_reply_xml(postdata['FromUserName'], postdata['ToUserName'], int(time.time()),
                                               u'test'), nonce)
                return text[1]
        else:
            print decrypt_data[0]

    @http.route('/ycloud_base/qy_auth/<key>', auth='none', methods=['post', 'get'],csrf=False)
    def set_qy_auth(self, **kw):
        env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        print kw
        suiteId = kw['key']
        auth_code = kw['auth_code']
        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',suiteId),('auth_component_platfromtype','!=','openplatform')])
        if len(third_platform)==0:
            symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
            appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
            token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
            if suiteId == 'tjeaae807dcefd96c8':
                appsercret = "lok8-TQ1d3n1pUZW86nKiG-b3DUYHdAwGwnDPQj23U15I_iOxHhOi5HATn8GJvem"
            elif suiteId=="tj0072de65cebdab77":
                appsercret="SoJ4APxNnhpSlqcQ5u-lpnE_fUP0t2t_XfbMMr_eL-kEl-1v0sDfhn4kkdBDBF0D"
        else:
            symmetric_key=third_platform[0]['auth_component_encodingasekey']
            appsercret=third_platform[0]['auth_component_appsecret']
            token=third_platform[0]['auth_component_token']
        key = suiteId + "suite_access_token"
        suite_access_token = cache.redis.get(key)
        permanent_code_info = qy_open_public_sdk.get_permanent_code(suite_access_token, suiteId, auth_code)
        print permanent_code_info
        permanent_code = permanent_code_info['permanent_code']
        corpid = permanent_code_info['auth_corp_info']['corpid']
        corp_name = permanent_code_info['auth_corp_info']['corp_name']
        auth_code_access_token = permanent_code_info['access_token']
        corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId, corpid,
                                                                     permanent_code)
        print corp_access_token
        qyh = env['wx.qyh'].search([('wx_qyh_id', '=', corpid)])
        if len(qyh) == 0:
            data = {}
            data.update({
                "wx_qyh_id": corpid,
                "wx_qyh_name": corp_name,
                'register_email':permanent_code_info['auth_user_info']['email']
            })
            qyh = env['wx.qyh'].create(data)
            qyh_id=qyh.id
            pass
        else:
            qyh_id = qyh.id
        print qyh_id
        if len(permanent_code_info['auth_info']['agent']) == 0:
            officialaccount = env['wx.officialaccount'].search(
                [('wx_appid', '=', corpid),  ('auth_component', '=', third_platform[0].id),('is_auth_officialaccount','=',True),('is_qyhapp','=',True)])
            print officialaccount
            if len(officialaccount) == 0:
                data = {}
                data.update({
                    'is_auth_officialaccount': True,
                    "is_qyhapp": True,
                    "wx_appid": corpid,
                    "wx_name": third_platform[0].auth_component_platformname,
                    "wx_qyh_app_id": 0,
                    "third_auth_id": 1,
                    "auth_component": third_platform[0].id,
                    "wx_qyh": qyh_id,
                    "third_auth_code": permanent_code_info['permanent_code']
                })
                print data
                try:
                    create_result = env['wx.officialaccount'].create(data)
                    _logger.debug(create_result)
                except Exception as e:
                    _logger.error('创建企业号应用出错:' + str(e))
                    print e
            else:
                data = {}
                data.update({
                    "third_auth_code": permanent_code_info['permanent_code']
                })
                officialaccount[0].write(data)
        for agent in permanent_code_info['auth_info']['agent']:
            officialaccount = env['wx.officialaccount'].search(
                [('wx_appid', '=', corpid), ('auth_component', '=', third_platform[0].id),
                 ('third_auth_id', '=', agent['appid']),('is_auth_officialaccount','=',True),('is_qyhapp','=',True)])
            if len(officialaccount) == 0:
                data = {}
                data.update({
                    'is_auth_officialaccount': True,
                    "is_qyhapp": True,
                    "wx_appid": corpid,
                    "wx_name": agent['name'],
                    "wx_qyh_app_id": agent['agentid'],
                    "third_auth_id": agent['appid'],
                    "auth_component": third_platform[0].id,
                    "wx_qyh": qyh_id,
                    "third_auth_code": permanent_code_info['permanent_code']
                })
                try:
                    create_result = env['wx.officialaccount'].create(data)
                    _logger.debug(create_result)
                except Exception as e:
                    _logger.error('创建企业号应用出错:' + str(e))
                    print e
            else:
                data = {}
                data.update({
                    "third_auth_code": permanent_code_info['permanent_code'],
                    "third_auth_name": agent['name']
                })
                officialaccount[0].write(data)
        #return 'sucess'
        return env_jinjia.get_template("register.html").render({
        })

    @http.route('/ycloud_base/userpay_message/<key>', auth='none', methods=['post', 'get'],csrf=False)
    def message(self, **kw):
        print http.request.httprequest.data
        print kw
        data = http.request.httprequest.data
        corpid = kw['key']
        env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',corpid),('auth_component_platfromtype','!=','openplatform')])
        if len(third_platform)==0:
            symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
            appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
            token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
            if corpid == 'tjeaae807dcefd96c8':
                appsercret = "lok8-TQ1d3n1pUZW86nKiG-b3DUYHdAwGwnDPQj23U15I_iOxHhOi5HATn8GJvem"
            elif corpid=="tj0072de65cebdab77":
                appsercret="SoJ4APxNnhpSlqcQ5u-lpnE_fUP0t2t_XfbMMr_eL-kEl-1v0sDfhn4kkdBDBF0D"
        else:
            symmetric_key=third_platform[0]['auth_component_encodingasekey']
            appsercret=third_platform[0]['auth_component_appsecret']
            token=third_platform[0]['auth_component_token']
        print data
        print corpid
        result = http.request.httprequest.url.split('?')[-1]
        msg_signature = ""
        timestamp = ""
        nonce = ""
        postdata = {}
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
        # token=unquote(token)
        # timestamp=unquote(timestamp)
        # msg_signature=unquote(msg_signature)
        # wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,appid)
        # symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
        # appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
        # token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
        data = http.request.httprequest.data
        print data
        xmldata = {}
        for el in etree.fromstring(data):
            xmldata[el.tag] = el.text
        appid = xmldata['ToUserName']
        # print "appid"+appid
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key, appid)
        decrypt_data = wXBizMsgCrypt.DecryptMsg(data, msg_signature, timestamp, nonce)
        print decrypt_data
        if decrypt_data[0] == 0:
            for el in etree.fromstring(decrypt_data[1]):
                postdata[el.tag] = el.text
            print postdata
            msgType = postdata['MsgType']
            fromUser = postdata['FromUserName']
            toUser = postdata['ToUserName']
            result = ""
            if msgType == "event":
                result = self.handler_event(postdata, wXBizMsgCrypt)
            elif msgType == "text":
                result = self.handler_text(postdata, wXBizMsgCrypt)
            # elif msgType == "image":
            #     result= self.handler_image(postdata)
            # elif msgType == "voice":
            #     result= self.handler_voice(postdata)
            # elif msgType == "video":
            #     result= self.handler_video(postdata, cr, uid)
            # elif msgType == "link":
            #     result= self.handler_link(postdata, cr, uid)
            # elif msgType == "location":
            #     result= self.handler_location(postdata, cr, uid)
            # elif msgType == "shortvideo":
            #     result= self.handler_shortvideo(postdata, cr, uid)
            else:
                messageinfo = reply_information.reply_information()
                content = u"默认未实现"
                result = messageinfo.text_reply_xml(fromUser, toUser, int(time.time()), content)
            print result
            result = wXBizMsgCrypt.EncryptMsg(result.encode('utf-8'), (nonce))
            print result
            return result[1]
        else:
            errcode = str(decrypt_data[0])
            encrypt_data = wXBizMsgCrypt.EncryptMsg(errcode, nonce)
            print encrypt_data[1]
            return encrypt_data[1]

    def handler_event(self, jsonStr, wXBizMsgCrypt):
        content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        AgentID=jsonStr['AgentID']
        eventType=jsonStr['Event']
        msgId = jsonStr['MsgId']
        key = msgId
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        if msgvalue == None:
            logging.info(u"服务号ID"+toUser)
            cache.redis.set(key, key,5000)
            if eventType=="CLICK":  #点击事件；
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
        # content = jsonStr['Content']
        # fromUser = jsonStr['FromUserName']
        # toUser = jsonStr['ToUserName']
        # AgentID=jsonStr['AgentID']
        # msgId = jsonStr['MsgId']
        # key = msgId
        # msgvalue = cache.redis.get(key)
        # messageinfo = reply_information.reply_information()
        # if msgvalue == None:
        #     cache.redis.set(key, key, 5000)
        #     print content
        #     env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        #     return env['receive_message'].accept_qy_message('ycloud.wx.message_text',jsonStr,AgentID)
        # else:
        #     return ""

    def handler_text(self, jsonStr, wXBizMsgCrypt):
        content = jsonStr['Content']
        fromUser = jsonStr['FromUserName']
        toUser = jsonStr['ToUserName']
        AgentID = jsonStr['AgentID']
        msgId = jsonStr['MsgId']
        key = msgId
        msgvalue = cache.redis.get(key)
        messageinfo = reply_information.reply_information()
        if msgvalue == None:
            cache.redis.set(key, key, 5000)
            print content
            env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
            return env['receive_message'].accept_qy_message('wx.message_text', jsonStr, AgentID)
        else:
            return ""

    @http.route('/ycloud_base/mananger/userpay', auth='none', methods=['post', 'get'],csrf=False)
    def userpay_manager(self, **kw):
        print kw
        print http.request.httprequest.data
        auth_code = kw['auth_code']
        symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
        appsercret = "UwUtt8En-jqhX-gd5tOrCC3Ym8_p0f54_vdIJ03H4tpn7gB7dEXGl2KXRCIVvwsc"
        token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
        suiteId = "tjb8b3ddf76ca38321"
        key = suiteId + "suite_access_token"
        suite_access_token = cache.redis.get(key)
        permanent_code_info = qy_open_public_sdk.get_permanent_code(suite_access_token, suiteId, auth_code)
        print permanent_code_info
        auth_info = qy_open_public_sdk.get_auth_info(suite_access_token, suiteId, 'wxe28ca91a338a7638', auth_code)
        print auth_info
        # permanent_code_info=qy_open_public_sdk.get_permanent_code(suite_access_token,suiteId,auth_code)
        # print permanent_code_info
        # permanent_code=permanent_code_info['permanent_code']
        # corpid=permanent_code_info['auth_corp_info']['corpid']
        # corp_name=permanent_code_info['auth_corp_info']['corp_name']
        # auth_code_access_token=permanent_code_info['access_token']
        corpid = 'wxe28ca91a338a7638'
        corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId, corpid, auth_code)
        print corp_access_token
        return 'success'
        # corpid="wxe28ca91a338a7638"
        # provider_secret="zV_Uc1zkcmJ7Uon1V7qZOhROPMPTIoO0LmqmrAYXbQRKhz1XjrBBswZhn3vidiZh"
        # provider_access_token=qy_open_public_sdk.get_provider_token(corpid,provider_secret)
        # print provider_access_token
        # auth_info=qy_open_public_sdk.get_login_info(auth_code,provider_access_token)
        # print auth_info
        # email=auth_info['user_info']['email']
        # auth_corpid=auth_info['corp_info']['corpid']
        # login_ticket=auth_info['redirect_login_info']['login_ticket']
        # print email
        # print auth_corpid
        # print login_ticket
        # agent_setting_url=qy_open_public_sdk.get_login_url(login_ticket,"agent_setting","",provider_access_token)
        # print agent_setting_url
        # send_msg_url=qy_open_public_sdk.get_login_url(login_ticket,"send_msg","",provider_access_token)
        # print send_msg_url
        # contact_url=qy_open_public_sdk.get_login_url(login_ticket,"contact","",provider_access_token)
        # print contact_url
        # third_admin_url=qy_open_public_sdk.get_login_url(login_ticket,"3rd_admin","",provider_access_token)
        # print third_admin_url
        # name="第三方软件"
        # return env.get_template("third_website.html").render({
        #     "title": name,
        #     'name': name,
        #     'redirect_url':agent_setting_url
        # })

    @http.route('/ycloud_base/auth_login', auth='none', methods=['post', 'get'],csrf=False)
    def auth_login(self, **kw):
        print kw
        auth_code = kw['auth_code']
        corpid = "wxe28ca91a338a7638"
        provider_secret = "zV_Uc1zkcmJ7Uon1V7qZOhROPMPTIoO0LmqmrAYXbQRKhz1XjrBBswZhn3vidiZh"
        provider_access_token = qy_open_public_sdk.get_provider_token(corpid, provider_secret)
        print provider_access_token
        auth_info = qy_open_public_sdk.get_login_info(auth_code, provider_access_token)
        print auth_info
        if str(auth_info['usertype']) == "1":  # 企业号创业者
            email = auth_info['user_info']['email']
            auth_corpid = auth_info['corp_info']['corpid']
            login_ticket = auth_info['redirect_login_info']['login_ticket']
            print email
            print auth_corpid
            print login_ticket
            agent_setting_url = qy_open_public_sdk.get_login_url(login_ticket, "agent_setting", "",
                                                                 provider_access_token)
            print agent_setting_url
            return werkzeug.utils.redirect(agent_setting_url)
        elif str(auth_info['usertype']) == "2":  # 企业号内部系统管理员
            userid = auth_info['user_info']['user_id']
            auth_corpid = auth_info['corp_info']['corpid']
            print userid
            print auth_corpid
            login_ticket = auth_info['redirect_login_info']['login_ticket']
            agent_setting_url = qy_open_public_sdk.get_login_url(login_ticket, "agent_setting", "",
                                                                 provider_access_token)
            print agent_setting_url
            return werkzeug.utils.redirect(agent_setting_url)
            pass
        elif str(auth_info['usertype']) == "3":  # 企业号外部系统管理员
            pass
        elif str(auth_info['usertype']) == "4":  # 企业号分级管理员
            pass
        elif str(auth_info['usertype']) == "5":  # 企业号成员
            userid = auth_info['user_info']['userid']
            username = auth_info['user_info']['name']
            auth_corpid = auth_info['corp_info']['corpid']
            return "欢迎" + username + "访问"
            pass
            # send_msg_url=qy_open_public_sdk.get_login_url(login_ticket,"send_msg","",provider_access_token)
            # print send_msg_url
            # contact_url=qy_open_public_sdk.get_login_url(login_ticket,"contact","",provider_access_token)
            # print contact_url
            # third_admin_url=qy_open_public_sdk.get_login_url(login_ticket,"3rd_admin","",provider_access_token)
            # print third_admin_url
            # name="第三方软件"
            # return env.get_template("third_website.html").render({
            #     "title": name,
            #     'name': name,
            #     'redirect_url':agent_setting_url
            # })
            # return 'success'

    @http.route('/ycloud_base/wechat', auth='none', methods=['post', 'get'],csrf=False)
    def wechat(self, **kw):
        env = Environment(http.request.cr, SUPERUSER_ID, http.request.context)
        data = http.request.httprequest.data
        print kw
        print data
        result = http.request.httprequest.url.split('?')[-1]
        msg_signature = ""
        timestamp = ""
        nonce = ""
        postdata = {}
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
        # token=unquote(token)
        # timestamp=unquote(timestamp)
        # msg_signature=unquote(msg_signature)
        # wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key,appid)
        suiteId = 'tjeaae807dcefd96c8'
        symmetric_key = "qspRg9bhytjI28Jb1gpAj8YDg9JGWHq4LFfqfNumla6"
        appsercret = "lok8-TQ1d3n1pUZW86nKiG-b3DUYHdAwGwnDPQj23U15I_iOxHhOi5HATn8GJvem"
        token = "64XiwF2VE8OA9oJiTGwr9YcrKPIRef"
        data = http.request.httprequest.data
        print data
        xmldata = {}
        for el in etree.fromstring(data):
            xmldata[el.tag] = el.text
        appid = xmldata['ToUserName']
        # print "appid"+appid
        wXBizMsgCrypt = WXBizMsgCrypt.WXBizMsgCrypt(token, symmetric_key, appid)
        decrypt_data = wXBizMsgCrypt.DecryptMsg(data, msg_signature, timestamp, nonce)
        print decrypt_data
        if decrypt_data[0] == 0:
            postdata = xmltodict.parse((decrypt_data[1]))['xml']
            # for el in etree.fromstring(decrypt_data[1]):
            #     postdata[el.tag] = el.text
            print postdata
            ItemCount = postdata['ItemCount']
            print ItemCount
            PackageId = postdata['PackageId']
            print PackageId
            Items = postdata['Item']
            print Items
            result = PackageId
            if 'AgentType' in postdata:
                count = (int)(ItemCount)
                if count == 1:
                    print postdata['Item']
                    MsgType = postdata['Item']['MsgType']
                    print MsgType
                    if MsgType == "event":
                        print postdata['Item']
                        pass
                    elif MsgType == "text":
                        FromUserName = postdata['Item']['FromUserName']
                        content2 = postdata['Item']['Content']
                        print FromUserName
                        Receiver_type = postdata['Item']['Receiver']['Type']
                        print Receiver_type
                        Receiver_ID = postdata['Item']['Receiver']['Id']
                        print Receiver_ID
                        MsgId=postdata['Item']['MsgId']
                        content = FromUserName + "说话的" + "文本消息内容是:" + content2 + "|" + str(int(time.time()))
                        key = suiteId + "suite_access_token"
                        suite_access_token = cache.redis.get(key)
                        third_platform=env['wx.third_platform'].search([('auth_component_appid','=',suiteId)])
                        officialaccount = env['wx.officialaccount'].search(
                            [('wx_appid', '=', appid), ('auth_component', '=', third_platform.id),
                             ('third_auth_id', '=', 1)])
                        text_template = {}
                        text_template.update({
                            "id": ""
                        })
                        try:
                            env['send_message'].insert_qy_text_record(FromUserName,officialaccount,env,content,text_template,"",False,"","sending","send")
                        except Exception as e:
                            _logger.info("插入文本消息记录出错:" + str(e))
                        corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                     appid,
                                                                                     officialaccount['third_auth_code'])
                        print corp_access_token
                        send_user = 'yinx'
                        receiver_type = 'group'
                        receiver_id = '9223372036864775811'
                        session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                              receiver_type, receiver_id)
                        print session_result
                    elif MsgType == "image":
                        FromUserName = postdata['Item']['FromUserName']
                        MediaId = postdata['Item']['MediaId']
                        PicUrl = postdata['Item']['PicUrl']
                        print FromUserName
                        Receiver_type = postdata['Item']['Receiver']['Type']
                        print Receiver_type
                        Receiver_ID = postdata['Item']['Receiver']['Id']
                        print Receiver_ID
                        # content =FromUserName+"说话的"+ "文本消息内容是:"+content2+"|" + str(int(time.time()))
                        content = FromUserName + "发送的图片地址为:" + PicUrl
                        key = suiteId + "suite_access_token"
                        suite_access_token = cache.redis.get(key)
                        officialaccount = env['wx.officialaccount'].search(
                            [('wx_appid', '=', appid), ('third_auth_SuiteId', '=', suiteId),
                             ('third_auth_id', '=', 1)])
                        corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                     appid,
                                                                                     officialaccount['third_auth_code'])
                        print corp_access_token
                        send_user = 'yinx'
                        receiver_type = 'group'
                        receiver_id = '9223372036864775811'
                        session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                              receiver_type, receiver_id)
                        print session_result
                        session_image_result = qy_open_public_sdk.send_image_session(corp_access_token, send_user,
                                                                                     MediaId,
                                                                                     receiver_type, receiver_id)
                        print session_image_result
                    elif MsgType == "voice":
                        FromUserName = postdata['Item']['FromUserName']
                        MediaId = postdata['Item']['MediaId']

                        print FromUserName
                        Receiver_type = postdata['Item']['Receiver']['Type']
                        print Receiver_type
                        Receiver_ID = postdata['Item']['Receiver']['Id']
                        print Receiver_ID
                        # content =FromUserName+"说话的"+ "文本消息内容是:"+content2+"|" + str(int(time.time()))
                        content = FromUserName + "发送的是语音。。。"
                        key = suiteId + "suite_access_token"
                        suite_access_token = cache.redis.get(key)
                        officialaccount = env['wx.officialaccount'].search(
                            [('wx_appid', '=', appid), ('third_auth_SuiteId', '=', suiteId),
                             ('third_auth_id', '=', 1)])
                        corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                     appid,
                                                                                     officialaccount['third_auth_code'])
                        print corp_access_token
                        send_user = 'yinx'
                        receiver_type = 'group'
                        receiver_id = '9223372036864775811'
                        session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                              receiver_type, receiver_id)
                        print session_result
                        session_image_result = qy_open_public_sdk.send_voice_session(corp_access_token, send_user,
                                                                                     MediaId,
                                                                                     receiver_type, receiver_id)
                        print session_image_result
                else:
                    for i in range(count):
                        print postdata['Item'][i]
                        MsgType = postdata['Item'][i]['MsgType']
                        print MsgType
                        if MsgType == "event":
                            print postdata['Item'][i]
                            pass
                        elif MsgType == "text":
                            FromUserName = postdata['Item'][i]['FromUserName']
                            print FromUserName
                            content2 = postdata['Item']['Content']
                            Receiver_type = postdata['Item'][i]['Receiver']['Type']
                            print Receiver_type
                            Receiver_ID = postdata['Item'][i]['Receiver']['Id']
                            print Receiver_ID
                            content = FromUserName + "说话的" + "文本消息内容是:" + content2 + "|" + str(int(time.time()))
                            key = suiteId + "suite_access_token"
                            suite_access_token = cache.redis.get(key)
                            officialaccount = env['wx.officialaccount'].search(
                                [('wx_appid', '=', appid), ('third_auth_SuiteId', '=', suiteId),
                                 ('third_auth_id', '=', 1)])
                            text_template = {}
                            text_template.update({
                                "id": ""
                                })
                            try:
                                env['send_message'].insert_qy_text_record(FromUserName,officialaccount,env,content,text_template,"",False,"","sending","send")
                            except Exception as e:
                                _logger.info("插入文本消息记录出错:" + str(e))
                            corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                         appid,
                                                                                         officialaccount[
                                                                                             'third_auth_code'])
                            print corp_access_token
                            send_user = 'yinx'
                            receiver_type = 'group'
                            receiver_id = '9223372036864775811'
                            session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                                  receiver_type, receiver_id)
                            print session_result
                        elif MsgType == "image":
                            FromUserName = postdata['Item'][i]['FromUserName']
                            MediaId = postdata['Item'][i]['MediaId']
                            PicUrl = postdata['Item'][i]['PicUrl']
                            print FromUserName
                            Receiver_type = postdata['Item'][i]['Receiver']['Type']
                            print Receiver_type
                            Receiver_ID = postdata['Item'][i]['Receiver']['Id']
                            print Receiver_ID
                            # content =FromUserName+"说话的"+ "文本消息内容是:"+content2+"|" + str(int(time.time()))
                            content = FromUserName + "发送的图片地址为:" + PicUrl
                            key = suiteId + "suite_access_token"
                            suite_access_token = cache.redis.get(key)
                            officialaccount = env['wx.officialaccount'].search(
                                [('wx_appid', '=', appid), ('third_auth_SuiteId', '=', suiteId),
                                 ('third_auth_id', '=', 1)])
                            corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                         appid,
                                                                                         officialaccount[
                                                                                             'third_auth_code'])
                            print corp_access_token
                            send_user = 'yinx'
                            receiver_type = 'group'
                            receiver_id = '9223372036864775811'
                            session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                                  receiver_type, receiver_id)
                            print session_result
                            session_image_result = qy_open_public_sdk.send_image_session(corp_access_token, send_user,
                                                                                         MediaId,
                                                                                         receiver_type, receiver_id)
                            print session_image_result
                        elif MsgType == "voice":
                            FromUserName = postdata['Item'][i]['FromUserName']
                            MediaId = postdata['Item'][i]['MediaId']

                            print FromUserName
                            Receiver_type = postdata['Item'][i]['Receiver']['Type']
                            print Receiver_type
                            Receiver_ID = postdata['Item'][i]['Receiver']['Id']
                            print Receiver_ID
                            # content =FromUserName+"说话的"+ "文本消息内容是:"+content2+"|" + str(int(time.time()))
                            content = FromUserName + "发送的是语音。。。"
                            key = suiteId + "suite_access_token"
                            suite_access_token = cache.redis.get(key)
                            officialaccount = env['wx.officialaccount'].search(
                                [('wx_appid', '=', appid), ('third_auth_SuiteId', '=', suiteId),
                                 ('third_auth_id', '=', 1)])
                            corp_access_token = qy_open_public_sdk.get_corp_access_token(suite_access_token, suiteId,
                                                                                         appid,
                                                                                         officialaccount[
                                                                                             'third_auth_code'])
                            print corp_access_token
                            send_user = 'yinx'
                            receiver_type = 'group'
                            receiver_id = '9223372036864775811'
                            session_result = qy_open_public_sdk.send_text_session(corp_access_token, send_user, content,
                                                                                  receiver_type, receiver_id)
                            print session_result
                            session_image_result = qy_open_public_sdk.send_voice_session(corp_access_token, send_user,
                                                                                         MediaId,
                                                                                         receiver_type, receiver_id)
                            print session_image_result
            print result
            return result
            result = wXBizMsgCrypt.EncryptMsg(result.encode('utf-8'), (nonce))
            print result
            return result[1]
        else:
            errcode = str(decrypt_data[0])
            encrypt_data = wXBizMsgCrypt.EncryptMsg(errcode, nonce)
            print encrypt_data[1]
            return encrypt_data[1]
        return 'success'
