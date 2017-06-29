# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging

logger = logging.getLogger(__name__)


def query_order_access_token(status, begintime, endtime, access_token):
    logger.debug("query_order_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/order/getbyfilter?access_token=" + access_token
    postdata = {}
    if status != 0:
        postdata.update({
            "status": status
        })
    if begintime != 0:
        postdata.update({
            "begintime": begintime
        })
    if endtime != 0:
        postdata.update({
            "endtime": endtime
        })
    req = urllib2.Request(category_url, json.dumps(postdata, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    return tokeninfo


def query_orderbyid(orderid, access_token):
    logger.debug("query_orderbyid_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/order/getbyid?access_token=" + access_token
    postdata = {}
    postdata.update({
        "order_id": orderid
    })
    req = urllib2.Request(category_url, json.dumps(postdata, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    return tokeninfo


def set_delivery_order_access_token(order_id, delivery_company, delivery_track_no, need_delivery, is_others,
                                    access_token):
    logger.debug("query_order_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/order/setdelivery?access_token=" + access_token
    postdata = {}
    postdata.update({
        "order_id": order_id,
        "delivery_company": delivery_company,
        "delivery_track_no": delivery_track_no,
        "need_delivery": need_delivery,
        "is_others": is_others
    })
    req = urllib2.Request(category_url, json.dumps(postdata, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    return tokeninfo


class order_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appsercret = AppSercret

    def query_order(self, status, begintime, endtime):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return query_order_access_token(status, begintime, endtime, access_token)

    def query_orderbyid(self, orderid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return query_orderbyid(orderid, access_token)

    def set_delivery_order(self, order_id, delivery_company, delivery_track_no, need_delivery, is_others):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appsercret)
        access_token = wx_public.getAccessToken()
        return set_delivery_order_access_token(order_id, delivery_company, delivery_track_no, need_delivery, is_others,
                                               access_token)
