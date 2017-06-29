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


def modify_stock_qty_access_token(product_id, sku_info, qty, access_token):
    logger.debug("modify_product_info_access_token:" + access_token)  # 默认增加库存
    modify_stock_url = "https://api.weixin.qq.com/merchant/stock/add?access_token=" + access_token
    if qty < 0:
        # 减少库存
        modify_stock_url = "https://api.weixin.qq.com/merchant/stock/reduce?access_token=" + access_token
    product_stock_data = {
        "product_id": product_id,
        "sku_info": sku_info,
        "quantity": abs(qty)
    }
    data = json.dumps(product_stock_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(modify_stock_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    modify_stock_qty_result = json.loads(html)
    print modify_stock_qty_result
    return modify_stock_qty_result


def modify_product_info_access_token(self, categoryid, product_name, product_id, main_img, imglist, detailist,
                                     buy_limit,
                                     sku_info, sku_list,
                                     isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace, delivery_info,
                                     location, access_token):
    logger.debug("modify_product_info_access_token:" + access_token)
    modify_product_url = "https://api.weixin.qq.com/merchant/update?access_token=" + access_token
    detaillistinfo = ""
    imglistinfo = imglist
    print imglistinfo
    if len(detailist) == 0:
        detaillistinfo = []
    else:
        for detail in detailist:
            detaillistinfo += str(detail) + ","
        detaillistinfo = eval(detaillistinfo[:-1])
    print json.dumps(detaillistinfo)
    if len(sku_info) == 0:
        product_data = {
            "product_id": product_id,
            "product_base": {
                "category_id": [categoryid],
                "name": product_name,
                "main_img": main_img,
                "img": imglistinfo,
                "detail": detaillistinfo,
                "buy_limit": buy_limit
            },
            "sku_list": sku_list,
            "attrext": {
                "location":
                    {
                        "country": location['country'],
                        "province": location['province'],
                        "city": location['city'],
                        "address": location['address']
                    },
                "isPostFree": isPostFree,
                "isHasReceipt": isHasReceipt,
                "isUnderGuaranty": isUnderGuaranty,
                "isSupportReplace": isSupportReplace
            },
            "delivery_info": delivery_info
        }
    else:
        product_data = {
            "product_id": product_id,
            "product_base": {
                "category_id": [categoryid],
                "name": product_name,
                "sku_info": sku_info,
                "detail": detaillistinfo,
                "buy_limit": buy_limit,
                "main_img": main_img,
                "img": imglist
            },
            "sku_list": sku_list,
            "attrext": {
                "location":
                    {
                        "country": location['country'],
                        "province": location['province'],
                        "city": location['city'],
                        "address": location['address']
                    },
                "isPostFree": isPostFree,
                "isHasReceipt": isHasReceipt,
                "isUnderGuaranty": isUnderGuaranty,
                "isSupportReplace": isSupportReplace
            },
            "delivery_info": delivery_info
        }
    data = json.dumps(product_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(modify_product_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    modify_product_result = json.loads(html)
    print modify_product_result
    return modify_product_result


def create_product_access_token(categoryid, product_name, main_img, imglist, detailist, propertylist, buy_limit,
                                sku_info,
                                sku_list, isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace, delivery_info,
                                location, access_token):
    logger.debug("create_product_access_token:" + access_token)
    create_product_url = "https://api.weixin.qq.com/merchant/create?access_token=" + access_token
    detaillistinfo = ""
    propertyinfo = ""
    imglistinfo = imglist
    print imglistinfo
    for detail in detailist:
        detaillistinfo += str(detail) + ","
    detaillistinfo = eval(detaillistinfo[:-1])
    print json.dumps(detaillistinfo)
    if len(propertylist) == 0:
        propertyinfo = []
    else:
        for propertys in propertylist:
            propertyinfo += str(propertys) + ","
        propertyinfo = eval(propertyinfo[:-1])
    if len(sku_info) == 0:
        product_data = {
            "product_base": {
                "category_id": [
                    categoryid
                ],
                "property": propertyinfo,
                "name": product_name,
                "main_img": main_img,
                "img": imglistinfo,
                "detail": detaillistinfo,
                "buy_limit": buy_limit
            },
            "sku_list": sku_list,
            "attrext": {
                "location":
                    {
                        "country": location['country'],
                        "province": location['province'],
                        "city": location['city'],
                        "address": location['address']
                    },
                "isPostFree": isPostFree,
                "isHasReceipt": isHasReceipt,
                "isUnderGuaranty": isUnderGuaranty,
                "isSupportReplace": isSupportReplace
            },
            "delivery_info": delivery_info
        }
    else:
        product_data = {
            "product_base": {
                "category_id": [
                    categoryid
                ],
                "property": propertylist,
                "name": product_name,
                "sku_info": sku_info,
                "main_img": main_img,
                "img": imglist,
                "detail": detaillistinfo,
                "buy_limit": buy_limit
            },
            "sku_list": sku_list,
            "attrext": {
                "location":
                    {
                        "country": location['country'],
                        "province": location['province'],
                        "city": location['city'],
                        "address": location['address']
                    },
                "isPostFree": isPostFree,
                "isHasReceipt": isHasReceipt,
                "isUnderGuaranty": isUnderGuaranty,
                "isSupportReplace": isSupportReplace
            },
            "delivery_info": delivery_info
        }
    data = json.dumps(product_data, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(create_product_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    create_product_result = json.loads(html)
    print create_product_result
    return create_product_result


def get_sub_property_access_token(categoryid, access_token):
    logger.debug("get_sub_property_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/category/getproperty?access_token=" + access_token
    category_data = {
        "cate_id": categoryid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo['properties']
    else:
        return "获取property错误:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def get_sub_sku_access_token(categoryid, access_token):
    logger.debug("get_sub_sku_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/category/getsku?access_token=" + access_token
    category_data = {
        "cate_id": categoryid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo['sku_table']
    else:
        return "获取SKU错误:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def del_product_access_token(productid, access_token):
    logger.debug("delete_product_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/del?access_token=" + access_token
    category_data = {
        "product_id": productid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    delete_result = json.loads(html)
    print delete_result
    return delete_result


def modify_product_status_access_token(productid, status, access_token):
    logger.debug("modify_product_status_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/modproductstatus?access_token=" + access_token
    category_data = {
        "product_id": productid,
        "status": status
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    product_result = json.loads(html)
    print product_result
    return product_result


def get_sub_category_access_token(categoryid, access_token):
    logger.debug("get_sub_category_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/category/getsub?access_token=" + access_token
    category_data = {
        "cate_id": categoryid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    print html
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo['cate_list']
    else:
        return "获取分类错误:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def upload_product_image_access_token(bufferdata, filename, access_token):
    uploadurl = "https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=" + access_token
    file_suffix = ".png"
    # req=urllib2.Request(uploadurl,urllib.urlencode(bufferdata))
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


def get_product_info_access_token(productid, access_token):
    logger.debug("get_sub_category_access_token:" + access_token)
    category_url = "https://api.weixin.qq.com/merchant/get?access_token=" + access_token
    category_data = {
        "product_id": productid
    }
    req = urllib2.Request(category_url, json.dumps(category_data, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    logger.debug('html:' + html)
    print html
    tokeninfo = json.loads(html)
    return tokeninfo


class product_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    # 库存管理接口
    def modify_stock_qty(self, product_id, sku_info, qty):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return modify_stock_qty_access_token(product_id, sku_info, qty, access_token)

    def modify_product_info(self, categoryid, product_name, product_id, main_img, imglist, detailist, buy_limit,
                            sku_info, sku_list,
                            isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace, delivery_info, location):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return modify_product_info_access_token(categoryid, product_name, product_id, main_img, imglist, detailist,
                                                buy_limit,
                                                sku_info, sku_list,
                                                isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace,
                                                delivery_info, location, access_token)

    def create_product(self, categoryid, product_name, main_img, imglist, detailist, propertylist, buy_limit, sku_info,
                       sku_list, isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace, delivery_info, location):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return create_product_access_token(categoryid, product_name, main_img, imglist, detailist, propertylist,
                                           buy_limit, sku_info,
                                           sku_list, isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace,
                                           delivery_info, location, access_token)

    def get_sub_property(self, categoryid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return get_sub_property_access_token(categoryid, access_token)

    def get_sub_sku(self, categoryid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return get_sub_property_access_token(categoryid, access_token)

    def delete_product(self, productid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return del_product_access_token(productid, access_token)

    def modify_product_status(self, productid, status):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return modify_product_status_access_token(productid, status, access_token)

    def get_sub_category(self, categoryid):
        print "get_sub_category"
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return get_sub_category_access_token(categoryid, access_token)

    def upload_product_image(self, bufferdata, filename):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return upload_product_image_access_token(bufferdata, filename, access_token)

    def get_productInfo(self, productid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return get_product_info_access_token(productid, access_token)
