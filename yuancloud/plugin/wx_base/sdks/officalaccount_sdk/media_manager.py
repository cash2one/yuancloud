# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

def get_media_access_token(mediaId, access_token):
    queryMenuUrl = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=" + access_token + "&media_id=" + mediaId
    response = urllib2.urlopen(queryMenuUrl)
    html = response.read()
    if 'errcode' in html:
        return ""
        # tokeninfo = json.loads(html)
        # print tokeninfo
    return response.headers['Content-Type'], html

def get_video_access_token(videoId, access_token):
    queryMenuUrl = "http://api.weixin.qq.com/cgi-bin/media/get?access_token=" + access_token + "&media_id=" + videoId
    response = urllib2.urlopen(queryMenuUrl)
    html = response.read()
    if 'errcode' in html:
        return ""
    # tokeninfo = json.loads(html)
    # print tokeninfo
    return response.headers['Content-Type'], html

def get_upload_image_access_token(bufferdata, file_suffix, access_token):
    try:
        uploadurl = "https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=" + access_token  # req=urllib2.Request(uploadurl,urllib.urlencode(bufferdata))
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        if file_suffix.lower() == ".png":
            data.append('Content-Disposition: form-data; name="%s"; filename="b.png"' % 'profile')
            data.append('Content-Type: %s\r\n' % 'image/png')
        else:
            data.append('Content-Disposition: form-data; name="%s"; filename="b.jpg"' % 'profile')
            data.append('Content-Type: %s\r\n' % 'image/jpg')
        data.append(bufferdata)
        data.append('--%s--\r\n' % boundary)
        http_body = '\r\n'.join(data)
        req = urllib2.Request(uploadurl, (http_body))
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
        # req.add_header('User-Agent','Mozilla/5.0')
        response = urllib2.urlopen(req)
        html = response.read().decode("utf-8")
        uploadresult = json.loads(html)
        return uploadresult
    except Exception as e:
        logger.error("上传图片出错:"+str(e))
        return {}

def get_upload_media2wx_access_token(mediatype, mediadata, accessToken):
    uploadurl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + accessToken + "&type=" + mediatype
    import requests
    files = {}
    if mediatype == "image":
        files = {'image': mediadata}
    elif mediatype == "voice":
        files = {'voice': mediadata}
    elif mediatype == "video":
        files = {'video': mediadata}
    res = requests.post(uploadurl, data=files)
    uploadresult = json.loads(res.content)
    print uploadresult
    return uploadresult

def get_upload_media_access_token(mediatype, mediaData, file_suffix, accessToken):
    uploadurl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=" + accessToken + "&type=" + mediatype
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    if file_suffix.lower() == ".png":
        data.append('Content-Disposition: form-data; name="%s"; filename="b.png"' % 'profile')
        data.append('Content-Type: %s\r\n' % 'image/png')
    elif file_suffix.lower() == ".jpg":
        data.append('Content-Disposition: form-data; name="%s"; filename="b.jpg"' % 'profile')
        data.append('Content-Type: %s\r\n' % 'image/jpg')
    elif file_suffix.lower() == ".amr":
        data.append('Content-Disposition: form-data; name="%s"; filename="b.amr"' % 'profile')
        data.append('Content-Type: %s\r\n' % 'audio')
    data.append(mediaData)
    data.append('--%s--\r\n' % boundary)
    http_body = '\r\n'.join(data)
    req = urllib2.Request(uploadurl, (http_body))
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    uploadresult = json.loads(html)
    return uploadresult

class media_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    def get_media(self, mediaId):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return get_media_access_token(mediaId, accessToken)

    def get_video(self, videoId):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return get_video_access_token(videoId, accessToken)

    def upload_image(self, bufferdata, file_suffix):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return get_upload_image_access_token(bufferdata, file_suffix, access_token)

    def upload_media2wx(self, mediatype, mediadata):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return get_upload_media2wx_access_token(mediatype, mediadata,accessToken)

    def upload_media(self, mediatype, mediaData, file_suffix):
        wxsdk = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        accessToken = wxsdk.getAccessToken()
        return get_upload_media_access_token(mediatype,mediaData,file_suffix,accessToken)
