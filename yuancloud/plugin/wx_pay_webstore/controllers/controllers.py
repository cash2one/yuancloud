# -*- coding: utf-8 -*-
from yuancloud import http
from yuancloud.http import request
from yuancloud.addons.wx_base.models import util
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import wx_public_sdk
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import js_sign
import logging
import time
import urllib2
import urlparse
from lxml import etree
from yuancloud import  SUPERUSER_ID
import pprint
from yuancloud.addons.payment.models.payment_acquirer import ValidationError
try:
    import simplejson as json
except ImportError:
    import json
from yuancloud import cache
from yuancloud.api import Environment

_logger = logging.getLogger(__name__)

def exec_pay_signature(app_id, package, officalaccount):
    app_sercert = ""
    app_key = ""
    mch_id = ""
    if officalaccount:
        mch_id=officalaccount.wx_mch_id
        mch_key=officalaccount.wx_mch_secret
        app_sercert=officalaccount.wx_appsecret
        data_post = {}
        data_post.update(
            {
                'package': "prepay_id=" + package,
                'timeStamp': str(int(time.time())),
                'nonceStr': util.random_generator(),
                'appId': app_id,
                'signType': "MD5"
            }
        )
        _, prestr = util.params_filter(data_post)
        print prestr
        data_post['paySign'] = util.build_mysign(prestr, mch_key, 'MD5')
        result = json.dumps(data_post)
        print result
        return result
    else:
        msg = "服务号信息出错"
        raise ValidationError("%s,%s" % (msg, ""))


def exec_signature(app_id, url, officalaccount):
    app_sercert = ""
    app_key = ""
    mch_id = ""
    if officalaccount:
        mch_id=officalaccount.wx_mch_id
        mch_key=officalaccount.wx_mch_secret
        app_sercert=officalaccount.wx_appsecret
        public_sdk = wx_public_sdk.wx_public_sdk(app_id, app_sercert)
        js_api_ticket = public_sdk.get_jsapi_ticket()
        print js_api_ticket
        jssign = js_sign.js_sign(js_api_ticket, url)
        result = jssign.gen_js_sign()
        print result
        return (result)
    else:
        return {}

class WxPayment(http.Controller):

    _notify_url = '/payment/weixin/notify/'

    @http.route('/payment/weixin/process', type='http', auth='none', methods=['POST', 'GET'], website=True,csrf=False)
    def process(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        parmsdata = request.params
        print parmsdata
        appid = parmsdata['appid']
        mch_id = parmsdata['mch_id']
        env = Environment(request.cr, SUPERUSER_ID, context)
        officialaccount = env['wx.officialaccount'].search([('wx_appid', '=', appid),('wx_mch_id','=',mch_id)])
        if officialaccount:
            appkey = officialaccount[0]['wx_mch_secret']
        else:
            appkey=""
        nonce_str = parmsdata['noncestr']
        body = parmsdata['body']
        out_trade_no = parmsdata['out_trade_no'],
        total_fee = parmsdata['total_fee']
        spbill_create_ip = parmsdata['spbill_create_ip']
        notify_url = parmsdata['notify_url']
        trade_type = parmsdata['trade_type']
        product_id = parmsdata['product_id']
        process_url = parmsdata['process_url']
        notify_url_address=self._notify_url+"db:"+cr.dbname
        data_post = {}
        data_post.update(
            {
                'appid': appid,
                'mch_id': mch_id,
                'nonce_str': nonce_str,
                'body': body,
                'out_trade_no': body,
                'total_fee': total_fee,
                'spbill_create_ip': spbill_create_ip,
                'notify_url': urlparse.urljoin(notify_url, notify_url_address),
                'trade_type': trade_type,
                'product_id': product_id,
            }
        )
        if trade_type == "JSAPI":
            opendid = http.request.session['openid']
            print opendid
            data_post.update({
                'openid': opendid
            })
        _, prestr = util.params_filter(data_post)
        data_post['sign'] = util.build_mysign(prestr, appkey, 'MD5')
        print data_post
        data_xml = "<xml>" + util.json2xml(data_post) + "</xml>"
        print data_xml
        url = process_url
        requestdata = urllib2.Request(url, data_xml)
        result = util._try_url(requestdata, tries=3)
        weixin_tx_values = {}
        _logger.info("request to %s and the request data is %s, and request result is %s" % (url, data_xml, result))
        return_xml = etree.fromstring(result)
        print return_xml
        if return_xml.find('return_code').text == "SUCCESS":
            if return_xml.find('code_url') == None:
                if return_xml.find('prepay_id') == None:
                    err_code = return_xml.find('err_code').text
                    err_code_des = return_xml.find('err_code_des').text
                else:
                    urlinfo = "/shop/confirmation"
                    sale_order_id = request.session.get('sale_last_order_id')
                    if sale_order_id:
                        order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
                    else:
                        return request.redirect('/shop')
                    print order
                    data_info = {}
                    data_info.update({
                        "order": order,
                        "test": "",
                        "appid": appid,
                        "prepay_id": return_xml.find('prepay_id').text,
                        "trade_type": trade_type
                    })
                    request.website.sale_reset(context=context)  # 清除
                    return request.website.render("website_sale.confirmation", data_info)
                    # raise ValidationError("%s, %s" % (err_code, err_code_des))
            elif return_xml.find('code_url').text == False:
                err_code = return_xml.find('err_code').text
                err_code_des = return_xml.find('err_code_des').text
            else:
                weixin_tx_values['data_xml'] = data_xml
                qrcode = return_xml.find('code_url').text
                weixin_tx_values['qrcode'] = qrcode
                urlinfo = "/shop/confirmation"
                sale_order_id = request.session.get('sale_last_order_id')
                _logger.info("sale_order_id:"+str(sale_order_id))
                if sale_order_id:
                    order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
                else:
                    return request.redirect('/shop')
                print order
                data_info = {}
                data_info.update({
                    "order": order,
                    "test": qrcode,
                    "appid": appid,
                    "prepay_id": return_xml.find('prepay_id').text,
                    "trade_type": trade_type
                })
                request.website.sale_reset(context=context) # 清除
                return request.website.render("website_sale.confirmation", data_info)
        else:
            return_code = return_xml.find('return_code').text
            return_msg = return_xml.find('return_msg').text
            raise ValidationError("%s, %s" % (return_code, return_msg))

    def weixin_validate_data(self, postdata):
        cr, uid, context = request.cr, request.uid, request.context
        json = {}
        for el in etree.fromstring(postdata):
            json[el.tag] = el.text
        try:
            appid=json['appid']
            _KEY = request.env['payment.acquirer'].search([('weixin_officialaccount.wx_appid', '=', appid)])[0].weixin_officialaccount.wx_mch_secret
            print _KEY
        except:
            _KEY = "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9"
        txs = request.env['payment.transaction'].search([('reference', '=', json['out_trade_no'])])
        if not txs and len(txs) > 1 and txs[0].state == 'done':
            return 'success'
        _, prestr = util.params_filter(json)
        mysign = util.build_mysign(prestr, _KEY, 'MD5')
        if mysign != json.get('sign'):
            _logger.info("签名错误")
            return 'false'
        _logger.info('weixin: validated data')
        return request.registry['payment.transaction'].form_feedback(cr, SUPERUSER_ID, json, 'weixin',
                                                                     context=context)

    @http.route('/payment/weixin/notify/<key>', type='http', auth='none', methods=['POST'],csrf=False)
    def weixin_notify(self, **post):
        """ weixin Notify. """
        _logger.info('Beginning weixin notify form_feedback with post data %s', pprint.pformat(post))  # debug
        postdata = request.httprequest.data
        print postdata
        if self.weixin_validate_data(postdata):
            # werkzeug.utils.redirect("/shop/payment/validate")
            json = {}
            for el in etree.fromstring(postdata):
                json[el.tag] = el.text
            transaction_id = json['transaction_id']
            openid = json['openid']
            is_subscribe = json['is_subscribe']
            appid = json['appid']
            print appid
            out_trade_no = json['out_trade_no']
            msgvalue = cache.redis.get(transaction_id)
            if msgvalue == None:
                cache.redis.set(transaction_id, transaction_id, 50000)
                if is_subscribe.lower() == "y":
                    print '准备发送支付成功信息'
                    message_key = "merchant_order"
                    context = http.request.context
                    context.update({
                        "openid": openid
                    })
                    env = Environment(request.cr, SUPERUSER_ID, context)
                    officialaccount = request.env['payment.acquirer'].search([('weixin_officialaccount.wx_appid', '=', appid)])[0]
                    oe_order = env['sale.order'].search([('name', '=', out_trade_no)])[0]
                    product_model = env['ir.model'].search([('model', '=', 'sale.order')])[0]
                    model_instances = []
                    model_instance = {}
                    model_instance.update({
                        "id": product_model['id'],
                        "model_value": oe_order
                    })
                    model_instances.append(model_instance)
                    env['wx.message.send_event'].sendmessage_TriggeredbyCommand(message_key, model_instances,officialaccount)
                    pass
                return 'success'
            else:
                return ""
        else:
            return ''


    @http.route('/payment/weixin/paysign', type='http', auth='none', methods=['POST'],csrf=False)
    def gen_pay_sign(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        parmsdata = request.params
        app_id = parmsdata['appid']
        package = parmsdata['package']
        officalaccount = ""
        try:
            officalaccount = request.env['payment.acquirer'].search([('weixin_officialaccount.wx_appid', '=', app_id)])[0]
            print officalaccount
        except:
            officalaccount = ""
        return exec_pay_signature(app_id, package, officalaccount.weixin_officialaccount)

    @http.route('/payment/weixin/sign', type='http', auth='none', methods=['POST'],csrf=False)
    def gen_js_sign(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        parmsdata = request.params
        app_id = parmsdata['appid']
        url = parmsdata['url']
        officalaccount = ""
        try:
            officalaccount = request.env['payment.acquirer'].search([('weixin_officialaccount.wx_appid', '=', app_id)])[0]
            print officalaccount
        except:
            officalaccount = ""
        sign_info = exec_signature(app_id, url, officalaccount.weixin_officialaccount)
        return json.dumps(sign_info)


    @http.route('/shop/get_status/<int:sale_order_id>',type='json', auth='none', methods=['POST'],csrf=False)
    def payment_get_status(self, sale_order_id, **post):
        # cr, uid, context = request.cr, request.uid, request.context
        # message=""
        # order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        # assert order.id == request.session.get('sale_last_order_id')
        #
        # if not order:
        #     return {
        #         'state': 'error',
        #         'message': '<p>%s</p>' % _('There seems to be an error with your request.'),
        #     }
        #
        # tx_ids = request.registry['payment.transaction'].search(
        #     cr, SUPERUSER_ID, [
        #         '|', ('sale_order_id', '=', order.id), ('reference', '=', order.name)
        #     ], context=context)
        #
        # if not tx_ids:
        #     if order.amount_total:
        #         return {
        #             'state': 'error',
        #             'message': '<p>%s</p>' % _('There seems to be an error with your request.'),
        #         }
        #     else:
        #         state = 'done'
        #         message = ""
        #         validation = None
        # else:
        #     tx = request.registry['payment.transaction'].browse(cr, SUPERUSER_ID, tx_ids[0], context=context)
        #     state = tx.state
        #     if state == 'done':
        #         message = '<p>%s</p>' % _('Your payment has been received.')
        #     elif state == 'cancel':
        #         message = '<p>%s</p>' % _('The payment seems to have been canceled.')
        #     elif state == 'pending' and tx.acquirer_id.validation == 'manual':
        #         message = '<p>%s</p>' % _('Your transaction is waiting confirmation.')
        #         if tx.acquirer_id.post_msg:
        #             message += tx.acquirer_id.post_msg
        #     elif state == 'error':
        #         message = '<p>%s</p>' % _('An error occurred during the transaction.')
        #     else:
        #         message= '<p>%s</p>' % _('请您立即支付.')
        #     validation = tx.acquirer_id.validation
        #
        # return {
        #     'state': state,
        #     'message': message,
        #     'validation': validation
        # }
        cr, uid, context = request.cr, request.uid, request.context

        order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        assert order.id == request.session.get('sale_last_order_id')

        values = {}
        flag = False
        if not order:
            values.update({'not_order': True, 'state': 'error'})
        else:
            tx_ids = request.registry['payment.transaction'].search(
                cr, SUPERUSER_ID, [
                    '|', ('sale_order_id', '=', order.id), ('reference', '=', order.name)
                ], context=context)

            if not tx_ids:
                if order.amount_total:
                    values.update({'tx_ids': False, 'state': 'error'})
                else:
                    values.update({'tx_ids': False, 'state': 'done', 'validation': None})
            else:
                tx = request.registry['payment.transaction'].browse(cr, SUPERUSER_ID, tx_ids[0], context=context)
                state = tx.state
                flag = state == 'pending'
                values.update({
                    'tx_ids': True,
                    'state': state,
                    'validation': tx.acquirer_id.auto_confirm == 'none'
                })
        return values
        #return {'recall': flag, 'message': request.website._render("website_sale.order_state_message", values)}