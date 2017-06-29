# -*- coding: utf-8 -*-
import hashlib
import time
import os
import urllib2,json,urllib


class reply_information:
    
    #链接消息回复
    def link_reply_xml(self,fromUser,toUser,createtime,title,description,url):
        linkInfo=u"你发送的是链接，标题为："+title+u"；内容为："+description+u"；链接地址为："+url
        return self.text_reply_xml(fromUser,toUser,createtime,linkInfo)
        
    #图文消息回复
    def news_reply_xml(self,fromUser,to_username,createTime,news):
         news_num = len(news)
         item_xml=""
         xml = u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>{3}</ArticleCount>
            <Articles>
            '''.format(fromUser, to_username , createTime, news_num)
         num = news_num
         for num in range(0, news_num):
             item_xml += u'''<item>
                   <Title><![CDATA[{0}]]></Title>
                   <Description><![CDATA[{1}]]></Description>
                   <PicUrl><![CDATA[{2}]]></PicUrl>
                   <Url><![CDATA[{3}]]></Url>
                   </item>
                    '''.format(news[num]['title'], news[num]['description'], news[num]['picurl'], news[num]['url'])
         xml += item_xml                    
         xml += u"""</Articles></xml>"""
         return xml
                
    #文本消息回复            
    def text_reply_xml(self,fromUser,toUserName,createTime,content):
        #content=content.encode('utf8')
        #print content
        xml=u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{3}]]></Content>
            '''.format(fromUser,toUserName,createTime,content)
        xml+=u'''</xml>'''
        return xml
    
    #音乐消息回复
    def music_reply_xml(self,fromUser,toUserName,createTime,musicTitle,musicDesc,musicUrl,HQMusicUrl,media_id):
        xml=u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[music]]></MsgType>
            <Music>
            <Title><![CDATA[{3}]]></Title>
            <Description><![CDATA[{4}]]></Description>
            <MusicUrl><![CDATA[{5}]]></MusicUrl>
            <HQMusicUrl><![CDATA[{6}]]></HQMusicUrl>
            <ThumbMediaId><![CDATA[{7}]]></ThumbMediaId>
            </Music>
            </xml>
            '''.format(fromUser,toUserName,createTime,musicTitle,musicDesc,musicUrl,HQMusicUrl,media_id)
        return xml
    
    #图片回复
    def image_reply_xml(self,fromUser,toUserName,createTime,imageId):
        xml=u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[image]]></MsgType>
            <Image>
            <MediaId>{3}</MediaId>
            </Image>
           </xml>
           '''.format(fromUser,toUserName,createTime,imageId)
        return xml
    
    #视频回复
    def video_reply_xml(self,fromUser,toUserName,createTime,videoId,title,description):
        xml=u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[video]]></MsgType>
            <Video>
            <MediaId><![CDATA[{3}]]></MediaId>
            <Title><![CDATA[{4}]]></Title>
            <Description><![CDATA[{5}]]></Description>
            </Video> 
            </xml>
            '''.format(fromUser,toUserName,createTime,videoId,title,description)
        return xml
    
    #音频回复
    def audio_reply_xml(self,fromUser,toUserName,createTime,audioId):
        xml=u'''
            <xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[voice]]></MsgType>
            <Voice>
            <MediaId>{3}</MediaId>
            </Voice>
            </xml>
            '''.format(fromUser,toUserName,createTime,audioId)
        return xml

    def serice_reply_xml(self,fromUser,toUserName,createTime):
        xml=u'''
        <xml>
        <ToUserName><![CDATA[{0}]]></ToUserName>
        <FromUserName><![CDATA[{1}]]></FromUserName>
        <CreateTime>{2}</CreateTime>
        <MsgType><![CDATA[transfer_customer_service]]></MsgType>
        </xml>'''.format(fromUser,toUserName,createTime)
        return xml