# -*- coding: utf-8 -*-
import time
import os
import urllib2, json, urllib
import wx_public_sdk
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

_logger = logging.getLogger(__name__)


def del_card_acces_token(cardid, access_token):
    _logger.debug("del_card_unavailable_access_token:" + access_token)
    postdata = {
        "card_id": cardid
    }
    del_card_url = "https://api.weixin.qq.com/card/delete?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(del_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


def modifystock_card_access_token(cardid, increase_stock_value, reduce_stock_value, access_token):
    _logger.debug("modifystock_card_access_token:" + access_token)
    postdata = {
        "card_id": cardid,
        "increase_stock_value": increase_stock_value,
        "reduce_stock_value": reduce_stock_value
    }
    modifystock_card_url = "https://api.weixin.qq.com/card/modifystock?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(modifystock_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return "修改库存成功"
    else:
        return "修改库存失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def update_card_access_token(cardinfo, access_token):
    _logger.debug("update_card_access_token:" + access_token)
    print access_token
    update_cardinfo_url = "https://api.weixin.qq.com/card/update?access_token=" + access_token
    data = cardinfo.encode('utf8')  # json.dumps(cardinfo,ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(update_cardinfo_url, data)
    # req.add_header("Content-Type","application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


def update_cardinfo_access_token(cardid, description, prerogative, discount, access_token):
    _logger.debug("update_cardinfo_access_token:" + access_token)
    postdata = {
        "card_id": cardid,
        "member_card":
            {
                "custom_field1":
                    {
                        "name_type": "FIELD_NAME_TYPE_DISCOUNT",
                        "url": ""
                    },
                "prerogative": prerogative,
                "discount": discount,
                "base_info": {
                    "description": description
                }
            }
    }
    update_cardinfo_url = "https://api.weixin.qq.com/card/update?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(update_cardinfo_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return "更新特权信息成功"
    else:
        return "更新特权信息失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def setcard_unavailable_access_token(cardid, code, access_token):
    _logger.debug("setcard_unavailable_access_token:" + access_token)
    postdata = ""
    if cardid.strip():
        postdata = {
            "code": code,
            "card_id": cardid
        }
    else:
        postdata = {
            "code": code
        }
    setcard_unavailable_url = "https://api.weixin.qq.com/card/code/unavailable?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(setcard_unavailable_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return "设置卡劵失效成功"
    else:
        return "设置卡劵失效失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def setpaycell_access_token(cardid, is_open, access_token):
    _logger.debug("setpaycell_access_token:" + access_token)
    postdata = {
        "card_id": cardid,
        "is_open": is_open
    }
    setformurl = "https://api.weixin.qq.com/card/paycell/set?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(setformurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


def getuserInfo_access_token(cardid, code, access_token):
    _logger.debug("getuserInfo_access_token:" + access_token)
    postdata = {
        "card_id": cardid,
        "code": code
    }
    setformurl = "https://api.weixin.qq.com/card/membercard/userinfo/get?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(setformurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "获取卡劵信息失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def setcardform_access_token(cardid, access_token):
    _logger.debug("setcardform_access_token:" + access_token)
    postdata = {
        "card_id": cardid,
        "required_form": {
            "common_field_id_list": [
                "USER_FORM_INFO_FLAG_NAME",
                "USER_FORM_INFO_FLAG_MOBILE",
                "USER_FORM_INFO_FLAG_BIRTHDAY"
            ]
        },
        "optional_form":
            {
                "common_field_id_list": [
                    "USER_FORM_INFO_FLAG_EMAIL",
                    "USER_FORM_INFO_FLAG_DETAIL_LOCATION",
                    # "USER_FORM_INFO_FLAG_INCOME",
                    # "USER_FORM_INFO_FLAG_IDCARD",
                    # "USER_FORM_INFO_FLAG_EDUCATION_BACKGROUND",
                    "USER_FORM_INFO_FLAG_CAREER"
                    # "USER_FORM_INFO_FLAG_INDUSTRY",
                    # "USER_FORM_INFO_FLAG_HABIT"
                ]
            }
    }
    setformurl = "https://api.weixin.qq.com/card/membercard/activateuserform/set?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(setformurl, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    return tokeninfo


def getcardhtml_access_token(cardid, access_token):
    _logger.debug("getcardhtml_access_token:" + access_token)
    postdata = {
        "card_id": cardid
    }
    get_card_url = "https://api.weixin.qq.com/card/mpnews/gethtml?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(get_card_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo['content']
    else:
        return "获取卡劵信息失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def createlangpage_access_token(bannerurl, cardlist, page_title, can_share, access_token):
    _logger.debug("createlangpage_access_token:" + access_token)
    detaillistinfo = ""
    for detail in cardlist:
        detaillistinfo += str(detail) + ","
    detaillistinfo = eval(detaillistinfo[:-1])
    print detaillistinfo
    postdata = {
        "banner": bannerurl,
        "page_title": page_title,
        "can_share": can_share,
        "scene": "SCENE_QRCODE",
        "card_list": detaillistinfo
    }
    create_langpage_url = "https://api.weixin.qq.com/card/landingpage/create?access_token=" + access_token
    data = json.dumps(postdata, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(create_langpage_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo['url']
    else:
        return "创建货架失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def uploadlogo_access_token(bufferdata, file_suffix, access_token):
    _logger.debug("uploadlogo_access_token:" + access_token)
    uploadurl = "https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=" + access_token
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


def getcolors_access_token(access_token):
    colorurl = "https://api.weixin.qq.com/card/getcolors?access_token=" + access_token
    response = urllib2.urlopen(colorurl)
    html = response.read().decode("utf-8")
    colorresult = json.loads(html)
    if str(colorresult['errcode']) == "0":
        colors = colorresult['colors']
        return json.dumps(colors);
    else:
        return "获取卡劵色值出错:" + str(colorresult['errcode'])


def create_member_access_token(logo_url, code_type, brand_name, title, sub_title, color, notice, description,
                               quantity, date_type, begin_timestamp, end_timestamp, fixed_term, fixed_begin_term,
                               use_custom_code, bind_openid, service_phone, location_id_list, source, custom_url_name,
                               custom_url, custom_url_sub_title, promotion_url_name, promotion_url,
                               promotion_url_sub_title,
                               get_limit, can_share, can_give_friend, need_push_on_view, prerogative, supply_bonus,
                               bonus_url, supply_balance, balance_url, name_type, url, bonus_cleared, bonus_rules,
                               balance_rules, activate_url, wx_activate, auto_activate, discount, access_token):
    _logger.debug("create_member_card:access_token:" + access_token)
    activate_url_value = activate_url
    wx_activate_value = True
    if auto_activate == True:
        auto_activate_value = True
        wx_activate_value = False
    elif wx_activate == True:
        wx_activate_value = True
        auto_activate_value = False
        activate_url_value = ""
    else:
        auto_activate_value = False
        wx_activate_value = False
    member_card_url = "https://api.weixin.qq.com/card/create?access_token=" + access_token
    date_info = ""
    if date_type == "DATE_TYPE_FIX_TIME_RANGE":
        memberData = {
            "card":
                {
                    "card_type": "MEMBER_CARD",
                    "member_card": {
                        "base_info": {
                            "logo_url": logo_url,
                            "brand_name": brand_name,
                            "code_type": code_type,
                            "title": title,
                            "sub_title": sub_title,
                            "color": color,
                            "notice": notice,
                            "description": description,
                            "date_info": {
                                "type": date_type,
                                "begin_timestamp": begin_timestamp,
                                "end_timestamp": end_timestamp
                            },
                            "sku": {
                                "quantity": quantity
                            },
                            "get_limit": get_limit,
                            "use_custom_code": use_custom_code,
                            "can_give_friend": can_give_friend,
                            "location_id_list": location_id_list,
                            "custom_url_name": custom_url_name,
                            "custom_url": custom_url,
                            "custom_url_sub_title": custom_url_sub_title,
                            "promotion_url_name": promotion_url_name,
                            "promotion_url": promotion_url,
                            "need_push_on_view": need_push_on_view
                        },
                        "supply_bonus": supply_bonus,
                        "supply_balance": supply_balance,
                        "prerogative": prerogative,
                        "activate_url": activate_url,
                        "auto_activate": auto_activate_value,
                        "wx_activate": wx_activate_value,
                        "bonus_url": bonus_url,
                        "balance_url": balance_url,
                        "discount": discount,
                        "custom_field1":
                            {
                                "name_type": name_type,
                                "url": url
                            }
                    }
                }
        }
    elif date_type == "DATE_TYPE_FIX_TERM":
        memberData = {
            "card":
                {
                    "card_type": "MEMBER_CARD",
                    "member_card": {
                        "base_info": {
                            "logo_url": logo_url,
                            "brand_name": brand_name,
                            "code_type": code_type,
                            "title": title,
                            "sub_title": sub_title,
                            "color": color,
                            "notice": notice,
                            "description": description,
                            "date_info": {
                                "type": date_type,
                                "fixed_term": fixed_term,
                                "fixed_begin_term": fixed_begin_term
                            },
                            "sku": {
                                "quantity": quantity
                            },
                            "get_limit": get_limit,
                            "use_custom_code": use_custom_code,
                            "can_give_friend": can_give_friend,
                            "location_id_list": location_id_list,
                            "custom_url_name": custom_url_name,
                            "custom_url": custom_url,
                            "custom_url_sub_title": custom_url_sub_title,
                            "promotion_url_name": promotion_url_name,
                            "promotion_url": promotion_url,
                            "need_push_on_view": need_push_on_view
                        },
                        "supply_bonus": supply_bonus,
                        "supply_balance": supply_balance,
                        "prerogative": prerogative,
                        "activate_url": activate_url,
                        "auto_activate": auto_activate_value,
                        "wx_activate": wx_activate_value,
                        "bonus_url": bonus_url,
                        "balance_url": balance_url,
                        "discount": discount,
                        "custom_field1":
                            {
                                "name_type": name_type,
                                "url": url
                            }
                    }
                }
        }
    elif date_type == "DATE_TYPE_PERMANENT":
        if wx_activate_value == True:
            memberData = {
                "card":
                    {
                        "card_type": "MEMBER_CARD",
                        "member_card": {
                            "base_info": {
                                "logo_url": logo_url,
                                "brand_name": brand_name,
                                "code_type": code_type,
                                "title": title,
                                "sub_title": sub_title,
                                "color": color,
                                "notice": notice,
                                "description": description,
                                "date_info": {
                                    "type": date_type
                                },
                                "sku": {
                                    "quantity": quantity
                                },
                                "get_limit": get_limit,
                                "use_custom_code": use_custom_code,
                                "can_give_friend": can_give_friend,
                                "location_id_list": location_id_list,
                                "custom_url_name": custom_url_name,
                                "custom_url": custom_url,
                                "custom_url_sub_title": custom_url_sub_title,
                                "promotion_url_name": promotion_url_name,
                                "promotion_url": promotion_url,
                                "need_push_on_view": need_push_on_view
                            },
                            "supply_bonus": supply_bonus,
                            "supply_balance": supply_balance,
                            "prerogative": prerogative,
                            "activate_url": activate_url,
                            # "auto_activate":False,
                            "discount": discount,
                            "wx_activate": wx_activate_value,
                            "bonus_url": bonus_url,
                            "balance_url": balance_url,
                            "custom_field1":
                                {
                                    "name_type": name_type,
                                    "url": url
                                }
                        }
                    }
            }
        else:
            memberData = {
                "card":
                    {
                        "card_type": "MEMBER_CARD",
                        "member_card": {
                            "base_info": {
                                "logo_url": logo_url,
                                "brand_name": brand_name,
                                "code_type": code_type,
                                "title": title,
                                "sub_title": sub_title,
                                "color": color,
                                "notice": notice,
                                "description": description,
                                "date_info": {
                                    "type": date_type
                                },
                                "sku": {
                                    "quantity": quantity
                                },
                                "get_limit": get_limit,
                                "use_custom_code": use_custom_code,
                                "can_give_friend": can_give_friend,
                                "location_id_list": location_id_list,
                                "custom_url_name": custom_url_name,
                                "custom_url": custom_url,
                                "custom_url_sub_title": custom_url_sub_title,
                                "promotion_url_name": promotion_url_name,
                                "promotion_url": promotion_url,
                                "need_push_on_view": need_push_on_view
                            },
                            "supply_bonus": supply_bonus,
                            "supply_balance": supply_balance,
                            "prerogative": prerogative,
                            "activate_url": activate_url,
                            "discount": discount,
                            "auto_activate": auto_activate_value,
                            # "wx_activate":wx_activate_value,
                            "bonus_url": bonus_url,
                            "balance_url": balance_url,
                            "custom_field1":
                                {
                                    "name_type": name_type,
                                    "url": url
                                }
                        }
                    }
            }

    _logger.debug("memberdata:" + json.dumps(memberData))
    req = urllib2.Request(member_card_url, json.dumps(memberData, ensure_ascii=False).encode('utf8'))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    return tokeninfo


def query_card_info_access_token(card_id, access_token):
    query_card_url = "https://api.weixin.qq.com/card/get?access_token=" + access_token
    card_info = {
        "card_id": card_id
    }
    _logger.debug("card_id:" + json.dumps(card_info))
    req = urllib2.Request(query_card_url, json.dumps(card_info))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    return tokeninfo


def setwhitelist_card_access_token(openids, usernames, access_token):
    setwhitelist_url = "https://api.weixin.qq.com/card/testwhitelist/set?access_token=" + access_token
    if not usernames.strip():
        if len(openids):
            whitelist = {
                "openid": openids
            }
    elif len(openids) == 0:
        whitelist = {
            "username": [usernames]
        }
    else:
        whitelist = {
            "openid": openids,
            "username": [usernames]
        }
    _logger.debug("whitelist:" + json.dumps(whitelist))
    req = urllib2.Request(setwhitelist_url, json.dumps(whitelist))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return u"设置白名单成功"
    else:
        return "设置白名单失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def active_card_access_token(membership_number, code, card_id, activate_begin_time, activate_end_time, init_bonus,
                             init_balance, access_token):
    activate_url = "https://api.weixin.qq.com/card/membercard/activate?access_token=" + access_token
    activate_data = {
        "init_bonus": init_bonus,
        "init_balance": init_balance,
        "membership_number": membership_number,
        "code": code,
        "card_id": card_id,
        "activate_begin_time": activate_begin_time
    }
    req = urllib2.Request(activate_url, json.dumps(activate_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return u"激活会员卡成功"
    else:
        return "激活会员卡失败:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def update_card_bonus_info_access_token(code, card_id, add_bonus, record_bonus, add_balance, record_balance,
                                        access_token):
    update_member_card_bonus_info_url = "https://api.weixin.qq.com/card/membercard/updateuser?access_token=" + access_token
    member_card_bonusinfo = {
        "code": code,
        "card_id": card_id,
        "record_bonus": record_bonus,
        "add_bonus": add_bonus,
        "add_balance": add_balance,
        "record_balance": record_balance
    }
    data = json.dumps(member_card_bonusinfo, ensure_ascii=False).encode('utf8')
    print data
    req = urllib2.Request(update_member_card_bonus_info_url, data)
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    print tokeninfo
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "更新会员积分出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def getcardlist_access_token(openid, card_id, access_token):
    get_cardlist_url = "https://api.weixin.qq.com/card/user/getcardlist?access_token=" + access_token
    if card_id.strip():
        get_cardlist_data = {
            "openid": openid,
            "card_id": card_id
        }
    else:
        get_cardlist_data = {
            "openid": openid
        }
    req = urllib2.Request(get_cardlist_url, json.dumps(get_cardlist_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "获取卡劵列表出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def get_card_info_access_token(card_id, code, access_token):
    get_card_info_url = "https://api.weixin.qq.com/card/membercard/userinfo/get?access_token=" + access_token
    card_info_data = {
        "card_id": card_id,
        "code": code
    }
    req = urllib2.Request(get_card_info_url, json.dumps(card_info_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "获取会员信息出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def consume_card_access_token(code, card_id, access_token):
    consume_card_url = "https://api.weixin.qq.com/card/code/consume?access_token=" + access_token
    if card_id.strip():
        consume_card_info = {
            "code": code,
            "card_id": card_id
        }
    else:
        consume_card_info = {
            "code": code
        }
    req = urllib2.Request(consume_card_url, json.dumps(consume_card_info))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "核销卡劵出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


def create_card_qrcode_access_token(expire_seconds, code, card_id, openid, is_unique_code, outer_id, access_token):
    create_card_qrcode_url = "https://api.weixin.qq.com/card/qrcode/create?access_token=" + access_token
    create_card_qrcode_data = {
        "action_name": "QR_CARD",
        "expire_seconds": expire_seconds,
        "action_info": {
            "card": {
                "card_id": card_id,
                "code": code,
                "openid": openid,
                "is_unique_code": is_unique_code,
                "outer_id": outer_id
            }
        }
    }
    req = urllib2.Request(create_card_qrcode_url, json.dumps(create_card_qrcode_data))
    req.add_header("Content-Type", "application/json")
    response = urllib2.urlopen(req)
    html = response.read().decode("utf-8")
    tokeninfo = json.loads(html)
    if tokeninfo['errcode'] == 0:
        return tokeninfo
    else:
        return "创建会员卡二维码出错:" + str(tokeninfo['errcode']) + tokeninfo['errmsg']


class card_manager:
    def __init__(self, AppId, AppSercret):
        self._appid = AppId
        self._appSercret = AppSercret

    def del_card(self, cardid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return del_card_acces_token(cardid, access_token)

    def modifystock_card(self, cardid, increase_stock_value, reduce_stock_value):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return modifystock_card_access_token(cardid, increase_stock_value, reduce_stock_value, access_token)

    def update_card(self, cardinfo):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return update_card_access_token(cardinfo, access_token)

    def update_cardinfo(self, cardid, description, prerogative, discount):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return update_cardinfo_access_token(cardid, description, prerogative, discount, access_token)

    def setcard_unavailable(self, cardid, code):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return setcard_unavailable_access_token(cardid, code, access_token)

    def setpaycell(self, cardid, is_open):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return setpaycell_access_token(cardid, is_open, access_token)

    def getuserInfo(self, cardid, code):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return getuserInfo_access_token(cardid, code, access_token)

    def setcardform(self, cardid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return setcardform_access_token(cardid, access_token)

    def getcardhtml(self, cardid):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return getcardhtml_access_token(cardid, access_token)

    def createlangpage(self, bannerurl, cardlist, page_title, can_share):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return createlangpage_access_token(bannerurl, cardlist, page_title, can_share, access_token)

    def uploadlogo(self, bufferdata, file_suffix):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return uploadlogo_access_token(bufferdata, file_suffix, access_token)

    def getcolors(self):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return getcolors_access_token(access_token)

    def create_member_card(self, logo_url, code_type, brand_name, title, sub_title, color, notice, description,
                           quantity, date_type, begin_timestamp, end_timestamp, fixed_term, fixed_begin_term,
                           use_custom_code, bind_openid, service_phone, location_id_list, source, custom_url_name,
                           custom_url, custom_url_sub_title, promotion_url_name, promotion_url, promotion_url_sub_title,
                           get_limit, can_share, can_give_friend, need_push_on_view, prerogative, supply_bonus,
                           bonus_url, supply_balance, balance_url, name_type, url, bonus_cleared, bonus_rules,
                           balance_rules, activate_url, wx_activate, auto_activate, discount):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return create_member_access_token(logo_url, code_type, brand_name, title, sub_title, color, notice, description,
                                          quantity, date_type, begin_timestamp, end_timestamp, fixed_term,
                                          fixed_begin_term,
                                          use_custom_code, bind_openid, service_phone, location_id_list, source,
                                          custom_url_name,
                                          custom_url, custom_url_sub_title, promotion_url_name, promotion_url,
                                          promotion_url_sub_title,
                                          get_limit, can_share, can_give_friend, need_push_on_view, prerogative,
                                          supply_bonus,
                                          bonus_url, supply_balance, balance_url, name_type, url, bonus_cleared,
                                          bonus_rules,
                                          balance_rules, activate_url, wx_activate, auto_activate, discount,
                                          access_token)

    def query_card_info(self, card_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return query_card_info_access_token(card_id, access_token)

    def setwhitelist_card(self, openids, usernames):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return setwhitelist_card_access_token(openids, usernames, access_token)

    def activate_card(self, membership_number, code, card_id, activate_begin_time, activate_end_time, init_bonus,
                      init_balance):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return active_card_access_token(membership_number, code, card_id, activate_begin_time, activate_end_time,
                                        init_bonus,
                                        init_balance, access_token)

    def update_member_card_bonus_info(self, code, card_id, add_bonus, record_bonus, add_balance, record_balance):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return update_card_bonus_info_access_token(code, card_id, add_bonus, record_bonus, add_balance, record_balance,
                                                   access_token)

    def getcardlist(self, openid, card_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return getcardlist_access_token(openid, card_id, access_token)

    def get_card_info(self, card_id, code):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return get_card_info_access_token(card_id, code, access_token)

    def consume_card(self, code, card_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return consume_card_access_token(code, card_id, access_token)

    def create_card_qrcode(self, expire_seconds, code, card_id, openid, is_unique_code, outer_id):
        wx_public = wx_public_sdk.wx_public_sdk(self._appid, self._appSercret)
        access_token = wx_public.getAccessToken()
        return create_card_qrcode_access_token(expire_seconds, code, card_id, openid, is_unique_code, outer_id,
                                               access_token)
