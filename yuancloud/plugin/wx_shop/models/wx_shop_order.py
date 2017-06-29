# -*- coding: utf-8 -*-

# from openerp import models, fields, api

import itertools
from lxml import etree
import urllib2
import logging

try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
from yuancloud.osv.osv import osv
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import order_manager,user_manager,bill_manager
import struct
import os
import time
import pytz, datetime
from collections import defaultdict
_logger = logging.getLogger(__name__)
from yuancloud import http
import string
import random
from yuancloud import http
from yuancloud.api import Environment
import base64

# ********微信销售订单,继承虚拟基类base_saleorder**********
class wx_shop_order(models.Model):
    '''
    实体：微信小店订单
    '''
    _inherits = {'sale.order': 'oe_salesorder'}
    _name = 'wx.shop.order'
    oe_salesorder = fields.Many2one("sale.order", string="OE订单", required=True, readonly=True, ondelete="restrict")
    wx_shop = fields.Many2one("wx.shop", string="微信小店", readonly=True)
    is_micro_channel_ship = fields.Boolean(string="是否小店订单", readonly=True)
    # 订单信息部分
    order_id = fields.Char(string="订单号", readonly=True)
    order_status = fields.Selection(
        [('2', '待发货'), ('3', '已发货'), ('5', '已完成'), ('8', '维权完成'), ('100', '已备货'), ('105', '已退货'), ('110', '待退款'),
         ('115', '已退款')],
        string="订单状态")
    order_total_price = fields.Float(string="总价格", digits=(12, 2), readonly=True)
    order_create_time = fields.Datetime(string="创建时间", readonly=True)  #
    order_express_price = fields.Integer(string="运费价格", readonly=True)
    buyer_openid = fields.Char(string="买家微信ID", readonly=True)
    buyer_nick = fields.Char(string="买家昵称", readonly=True)
    # 收货信息部分
    receiver_name = fields.Char(string="收货人姓名", readonly=True)
    receiver_province = fields.Char(string="收货地址省份", readonly=True)
    receiver_city = fields.Char(string="收货地址城市", readonly=True)
    receiver_zone = fields.Char(string="收货地址区/县", readonly=True)
    receiver_address = fields.Char(string="收货详细地址", readonly=True)
    receiver_mobile = fields.Char(string="收货人移动电话", readonly=True)
    receiver_phone = fields.Char(string="收货人固定电话", readonly=True)
    # 商品信息部分
    product_id = fields.Char(string="商品ID", readonly=True)
    product_name = fields.Char(string="商品名称", readonly=True)
    product_price = fields.Float(string="商品价格", digits=(12, 2), readonly=True)
    product_sku = fields.Char(string="商品SKU", readonly=True)
    product_count = fields.Integer(string="商品个数", readonly=True)
    product_img = fields.Char(string="商品主图", readonly=True)
    # 运单信息部分
    delivery_id = fields.Char(string="运单ID", readonly=True)
    delivery_company = fields.Char(string="物流公司编码", readonly=True)
    # 交易信息部分
    trans_id = fields.Char(string="交易ID", readonly=True)
    tradetype = fields.Char(string="交易类型", readonly=True)
    tradestatus = fields.Char(string="交易状态", readonly=True)
    bank = fields.Char(string="付款银行", readonly=True)
    currency = fields.Char(string="货币种类", readonly=True)
    redpacketmoney = fields.Float(string="代金劵或立减优惠金额", readonly=True)
    fee = fields.Float(string="手续费", readonly=True)
    rate = fields.Float(string="费率", readonly=True)
    _order = 'create_date desc'

    @api.multi
    def unlink(self):
        '''
        功能：微信订单来自微信小店，不允许删除
        :return:
        '''
        result_success = ''
        result_error = ''
        for id in self.ids:
            obj = self.browse(id)
            if obj.order_status == '2':
                result_success = result_success + obj.name + ','
                super(wx_shop_order, obj).unlink()
                self._cr.commit()
            else:
                _logger.error("只有待发货状态的微信订单才可以删除")
                result_error = result_error + obj.name + ','
        if result_success != '':
            result_success = "微信订单：%s 删除成功" % result_success[:-1]
        if result_error != '':
            if result_success != '':
                result_error = "\n微信订单：%s 不是‘待发货’状态，不允许删除" % result_error[:-1]
            else:
                result_error = "微信订单：%s 不是‘待发货’状态，不允许删除" % result_error[:-1]
        msg = "%s%s" % (result_success, result_error)
        if result_error <> '':
            raise except_osv(_('提示'), _(msg))

    # ******************检查备货--Begin***********************
    @api.one
    def check_stocking(self, single):
        '''
        功能：检查备货核心方法
        :param single:
        :return:
        '''
        isSuccess = False
        msg = None
        try:
            exe_update = False
            # 检查库存作业（已备货、已退货、待退款）
            group_id = 0
            order_status = 100
            order_status_desp = '已备货'
            stock_pickings = self.env["stock.picking"].search([('origin', '=', self.oe_salesorder.name)])
            if len(stock_pickings) > 0:
                group_id = stock_pickings[0].group_id.id
                pickings = self.env["stock.picking"].search([('group_id', '=', group_id)])
                if len(pickings) > 0:
                    for picking in pickings:
                        if picking.state == 'done':
                            exe_update = True
                            break
                    if len(pickings) > 0 and pickings[0].picking_type_id == self.wx_shop.return_picking_type and \
                                    pickings[0].state == 'done':
                        order_status = 105
                        order_status_desp = '已退货'
                        #
                        account_invoices = self.env["account.invoice"].search(
                            [('origin', '=', self.oe_salesorder.name)])

            if exe_update:
                isSuccess = True
                self.write({'order_status': str(order_status)})
                self._cr.commit()
                if single:
                    msg = "微信订单%s %s" % (self.order_id, order_status_desp)
                    raise except_osv(_('提示'), _(msg))
            else:
                msg = '微信订单状态维持不变'
                _logger.info(msg)
                if single:
                    raise except_osv(_('提示'), _(msg))
                    # 检查库存作业（已备货、已退货、待退款）

        except Exception as e:
            _logger.error(e)
            if single:
                raise except_osv(_('提示'), _(msg))
            else:
                return isSuccess

    @api.one
    def signal_check_stocking(self):
        '''
        功能：单个检查备货
        :return:
        '''
        self.check_stocking(True)

    def batch_check_stocking(self, cr, uid, ids, context=None):
        '''
        功能：批量检查备货
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        '''
        result_success = ""
        success_count = 0
        error_count = 0
        for id in ids:
            try:
                wx_record = self.browse(cr, uid, id, context=context)
                isSuccess = wx_record.check_stocking(False)
                if isSuccess:
                    result_success = result_success + wx_record.order_id + ','
                    success_count = success_count + 1
                else:
                    error_count = error_count + 1
            except Exception as e:
                _logger.error(e)
                error_count = error_count + 1
        result_success = result_success[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "已备货的微信订单:" + result_success
        _logger.debug(result_msg)

        # 提示
        result_msg = "共%s单已备货,共%s单出现异常" % (success_count, error_count)
        if error_count > 0:
            result_msg = result_msg + "\n异常可能的原因：1.确实未备货；2.已发货；3.程序异常"
        raise except_osv(_('提示'), _(result_msg))

    # ******************检查备货--End***********************

    # ******************处理微信发货--Begin***********************
    # 发货
    def delivery_goods(self, single):
        isSuccess = False
        msg = None
        try:
            if self.order_status == '100':
                stock_pickings = self.env["stock.picking"].search([('origin', '=', self.oe_salesorder.name)])
                if len(stock_pickings) > 0:
                    if stock_pickings[0].state == 'done' and stock_pickings[0].carrier_id and stock_pickings[
                        0].carrier_tracking_ref:
                        wx_carriers = self.env['ycloud.base.carrier'].search(
                            [('oe_carrier', '=', stock_pickings[0].carrier_id.id)])
                        appid = self.wx_shop.wx_official_account.wx_appid
                        appsecret = self.wx_shop.wx_official_account.wx_appsecret
                        order_help = order_manager.order_manager(appid, appsecret)
                        result = {}
                        order_id = self.order_id
                        delivery_track_no = stock_pickings[0].carrier_tracking_ref
                        need_delivery = 1
                        if len(wx_carriers) > 0:
                            delivery_company = wx_carriers[0].wx_carrier_code
                            is_others = 0
                            result = order_help.set_delivery_order(order_id, delivery_company, delivery_track_no,
                                                                   need_delivery,
                                                                   is_others)
                        else:
                            # 其他物流公司
                            delivery_company = stock_pickings[0].carrier_id.name
                            is_others = 1
                            result = order_help.set_delivery_order(order_id, delivery_company, delivery_track_no,
                                                                   need_delivery,
                                                                   is_others)
                        if result["errcode"] == 0:
                            # 微信记录状态更改为已发货
                            self.write({'order_status': '3'})
                            # self._cr.commit()
                            if single:
                                msg = "微信订单：%s 发货成功" % self.order_id
                                # raise except_osv(_('提示'), _(msg))
                            else:
                                isSuccess = True
                        else:
                            msg = "微信订单：%s 发货失败，失败原因：%s" % (self.order_id, result["errmsg"])
                            _logger.info(result["errmsg"])
                            if single:
                                raise except_osv(_('提示'), _(msg))
                    else:
                        msg = "微信订单：%s 发货失败，失败原因：只有发货单状态为已转移且维护了物流公司及物流单号的才可进行发货处理" % self.order_id
                        _logger.info(msg)
                        if single:
                            raise except_osv(_('提示'), _(msg))
            elif self.order_status == '3':
                msg = "微信订单：%s 已发货，不允许重复发货" % self.order_id
                _logger.info(msg)
                if single:
                    raise except_osv(_('提示'), _(msg))
            else:
                msg = "微信订单：%s还未备货，不允许发货" % self.order_id
                _logger.info(msg)
                if single:
                    raise except_osv(_('提示'), _(msg))
            return isSuccess
        except Exception as e:
            if single:
                raise except_osv(_('提示'), _(msg))
            else:
                msg = "发货失败，原因：%s" % e.message
                _logger.error(msg)
                return isSuccess

    # 1.单个发货
    @api.one
    def signal_delivery_goods(self):
        self.delivery_goods(True)

    # 2.批量发货
    def batch_delivery_goods(self, cr, uid, ids, context=None):
        result_success = ""
        result_error = ""
        success_count = 0
        error_count = 0
        for id in ids:
            try:
                wx_record = self.browse(cr, uid, id, context=context)
                isSuccess = wx_record.delivery_goods(False)
                if isSuccess:
                    result_success = result_success + wx_record.order_id + ','
                    success_count = success_count + 1
                else:
                    result_error = result_error + wx_record.order_id + ','
                    error_count = error_count + 1
            except Exception as e:
                _logger.error(e)
                error_count = error_count + 1
        result_success = result_success[:-1]
        result_error = result_error[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "发货成功的微信订单:" + result_success
        if result_error != "":
            result_msg += "发货失败的微信订单:" + result_error
        _logger.debug(result_msg)

        # 提示
        result_msg = "共%s单发货成功,%s单发货出现异常" % (success_count, error_count)
        if error_count > 0:
            result_msg = result_msg + "\n异常可能原因：1.未备货；2.未维护物流公司及物流单号；3.程序异常"
        raise except_osv(_('提示'), _(result_msg))

    # ******************处理微信发货--End***********************

    # ******************处理微信确认退款--Begin***********************
    @api.one
    def signal_confirm_refund(self):
        pass
        # ******************处理微信确认退款--End***********************

# ************同步微小店订单--begin***********************
class wx_sync_shop_order(models.Model):
    _name = 'wx.syncorder'
    wx_shop = fields.Many2one("wx.shop", string="微信小店", required=True)
    timeperiod = fields.Selection([('1', '本日'), ('5', '最近七天'), ('10', '最近十五天')], string="时间周期", default='1')
    start_time = fields.Datetime(string="开始时间", required=True)
    end_time = fields.Datetime(string="结束时间", required=True)
    description = fields.Char("描述")
    # 小店订单状态
    order_status = fields.Selection([('2', '待发货'), ('3', '已发货'), ('5', '已完成'), ('8', '维权完成')], string="状态", default='2',
                                    readonly=True)

    @api.onchange('timeperiod')
    def set_time(self):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        current_time = fields.datetime.now()
        today = current_time.date()
        self.end_time = datetime.datetime.strftime(current_time, datetime_format)
        if self.timeperiod == '1':
            self.start_time = self.get_utc_time(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(today.timetuple()))))
        if self.timeperiod == '5':
            begin_date = today - datetime.timedelta(days=7)
            self.start_time = self.get_utc_time(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(begin_date.timetuple()))))
        if self.timeperiod == '10':
            begin_date = today - datetime.timedelta(days=15)
            self.start_time = self.get_utc_time(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(begin_date.timetuple()))))

    # 本时区时间转UTC时间
    def get_utc_time(self, dt):
        tz = self._context['tz']
        if tz:
            local = pytz.timezone(tz)
            naive = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            local_dt = local.localize(naive, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            return utc_dt
        else:
            return dt

    @api.one
    def sync_shop_order(self):
        '''
        功能：同步小店订单
        :return:
        '''
        try:
            env = Environment(self._cr, self._uid, self._context)
            if self.wx_shop.wx_official_account.wx_company.org_admin:
                env = Environment(self._cr, self.wx_shop.wx_official_account.wx_company.org_admin.id, self._context)
            count_days = self.datediff(self.start_time, self.end_time)
            if count_days > 15:
                error_msg = "只允许处理15天之内的数据！"
                raise except_osv(_('提示'), _(error_msg))
            datetime_format = '%Y-%m-%d %H:%M:%S'
            start_timeStamp = 0
            end_timeStamp = 0
            if self.start_time:
                start_timeArray = time.strptime(self.start_time, datetime_format)
                start_timeStamp = int(time.mktime(start_timeArray))
            if self.end_time:
                end_timeArray = time.strptime(self.end_time, datetime_format)
                end_timeStamp = int(time.mktime(end_timeArray))
            else:
                end_timeStamp = int(time.time())
            status = 0
            if self.order_status:
                status = int(self.order_status)

            appid = self.wx_shop.wx_official_account.wx_appid
            appsecret = self.wx_shop.wx_official_account.wx_appsecret
            pricelist_id = self.wx_shop.oe_pricelist.id  # 价目表
            order_help = order_manager.order_manager(appid, appsecret)
            result = order_help.query_order(status, start_timeStamp, end_timeStamp)
            if result['errcode'] == 0:
                all_count = len(result["order_list"])  #
                success_count = 0
                already_count = 0
                err_count = 0
                msg = "总共%s条" % all_count
                if all_count == 0:
                    msg = "暂无需要同步的微信订单"
                for order in result["order_list"]:
                    wx_record_instance = env['wx.shop.order']
                    wx_record = wx_record_instance.search_read([('order_id', '=', order["order_id"])])
                    if len(wx_record):
                        already_count = already_count + 1
                    else:
                        wx_product_obj = env['wx.product']
                        wx_products = wx_product_obj.search([('wx_productid', '=', order["product_id"])])
                        product_tmpl_id = 0
                        if len(wx_products) > 0:
                            product_tmpl_id = wx_products[0].oe_product.id
                        product_product_obj = env['product.product']
                        product_products = product_product_obj.search([('product_tmpl_id', '=', product_tmpl_id)])
                        if len(product_products) == 0:
                            err_count = err_count + 1
                        else:
                            company_id=False
                            if self.wx_shop.wx_official_account.wx_company:
                                company_id=self.wx_shop.wx_official_account.wx_company.id
                            #***************1.处理客户***********************
                            cus_values={}
                            cus_values['name']=order['receiver_name']
                            cus_values["province"] = order["receiver_province"]
                            cus_values['city']=order['receiver_city']
                            cus_values['street']=order["receiver_zone"] + order["receiver_address"]
                            cus_values['mobile']=order['receiver_mobile']
                            cus_values["phone"] = order["receiver_phone"]
                            cus_values["openid"] = order["buyer_openid"]
                            if self.wx_shop.sale_team:
                                cus_values['section_id']=self.wx_shop.sale_team.id
                                if self.wx_shop.sale_team.user_id:
                                    cus_values['user_id']=self.wx_shop.sale_team.user_id.id
                            param_value={}
                            param_value['official_account']=self.wx_shop.wx_official_account
                            param_value['company_id']=company_id

                            result_customer = self.create_customer(env,cus_values,param_value)

                            #**********************2.处理后续单据***********************************
                            product_sku = order["product_sku"]
                            product_id=False
                            for product in product_products:
                                if len(product_sku) == 0:
                                    product_id = product_products[0].id
                                else:
                                    if product_sku.replace('$', '') == product.attribute_value_ids.display_name.replace(' ', ''):
                                        product_id = product.id

                            unit_price=order['product_price']*0.01
                            product_num=order['product_count']
                            order_create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order["order_create_time"]))

                            #notice: order_value:后续单据所需数据
                            order_value = {}
                            order_value.update({
                                'delivery_type':'express',
                                'partner_id':result_customer["customer_id"],
                                'partner_invoice_id':result_customer["contact_id"],
                                'partner_shipping_id':result_customer["contact_id"],
                                'wx_customer_id':result_customer["wx_customer_id"],
                                'data_order':datetime.datetime.now(),
                                'order_policy':'manual',
                                'product_price':unit_price,
                                'order_total_price':unit_price * product_num,
                                'pricelist_id':pricelist_id,
                                'product_id':product_id,
                                'product_count':product_num,
                                'officialaccount_id':self.wx_shop.wx_official_account.id,
                                'trans_id':order['trans_id'],
                                'order_create_time':order_create_time
                            })
                            if company_id:
                                order_value.update({
                                    'company_id': company_id,
                                })
                            ##notice: order,小店订单所需数据
                            order.update({
                                'product_price':unit_price,
                                'order_total_price':unit_price * product_num,
                                'order_status':str(order["order_status"]),
                                'is_micro_channel_ship':True,
                                'wx_shop':self.wx_shop.id,
                                'order_create_time':order_create_time
                            })
                            result = self._create_after_order(env,order_value,order)
                            self._cr.commit()
                            result_mark=result['result_mark']
                            if result_mark == "Success":
                                success_count = success_count + 1
                            elif result_mark == "Already":
                                already_count = already_count + 1
                            else:
                                err_count = err_count + 1
                if success_count > 0:
                    msg = msg + ",成功%s条" % success_count
                if err_count > 0:
                    msg = msg + ",失败%s条" % err_count
                if already_count > 0:
                    msg = msg + ",已同步过的共%s条" % already_count
                msg = msg + "！"
                raise except_osv(_('提示'), _(msg))

            else:
                skd_error_msg = "调用微信获取订单详情接口报错:%s" % result['errmsg']
                raise except_osv(_('错误'), _(skd_error_msg))

        except Exception as e:
            _logger.error(e)
            raise e

    @api.model
    def create_record(self, order_id, product_id_err, wxOfficeAccountInfo):
        '''
        功能：从小店购买商品
        :param order_id:
        :param product_id_err:
        :param wxOfficeAccountInfo:
        :return:
        '''
        env = Environment(self._cr, self._uid, http.request.context)
        company_id=False
        org_admin=False
        if wxOfficeAccountInfo.wx_company:
            company_id=wxOfficeAccountInfo.wx_company.id
            org_admin=wxOfficeAccountInfo.wx_company.org_admin
        if org_admin:
            env = Environment(self._cr, org_admin.id, http.request.context)
            _logger.info('组织级管理员:%s' % org_admin.name)
        shop = env['wx.shop'].search([('wx_official_account', '=', wxOfficeAccountInfo['id'])])[0]
        appid = wxOfficeAccountInfo.wx_official_account_appid
        appsecret = wxOfficeAccountInfo.wx_official_account_appsecret
        pricelist_id = shop.oe_pricelist.id  # 价目表
        order_help = order_manager.order_manager(appid, appsecret)
        result = order_help.query_orderbyid(order_id)
        if result['errcode'] == 0:
            orderinfo = result['order']
            order = {}
            order.update({
                "product_id": orderinfo['product_id'],
                'product_name': orderinfo['product_name'],
                "buyer_openid": orderinfo['buyer_openid'],
                "buyer_nick": orderinfo['buyer_nick'],
                "receiver_zone": orderinfo['receiver_zone'],
                "receiver_address": orderinfo['receiver_address'],
                "receiver_name": orderinfo['receiver_name'],
                "receiver_city": orderinfo['receiver_city'],
                "receiver_mobile": orderinfo['receiver_mobile'],
                "receiver_phone": orderinfo['receiver_phone'],
                "receiver_province": orderinfo['receiver_province'],
                "product_price": orderinfo['product_price'],
                "order_total_price": orderinfo["order_total_price"],
                "product_count": orderinfo["product_count"],
                "order_status": orderinfo["order_status"],
                "order_create_time": orderinfo['order_create_time'],
                "product_sku": orderinfo['product_sku'],
                "order_id": orderinfo['order_id'],
                "trans_id":orderinfo['trans_id']
            })
            wx_product_obj = env['ycloud.wx.product']
            wx_products = wx_product_obj.search([('wx_productid', '=', order["product_id"])])
            product_tmpl_id = 0
            if len(wx_products) > 0:
                product_tmpl_id = wx_products[0].oe_product.id
            product_product_obj = env['product.product']
            product_products = product_product_obj.search([('product_tmpl_id', '=', product_tmpl_id)])
            if len(product_products) == 0:
                raise "产品错误"
            else:
                cus_values={}
                cus_values['name']=order['receiver_name']
                cus_values["province"] = order["receiver_province"]
                cus_values['city']=order['receiver_city']
                cus_values['street']=order["receiver_zone"] + order["receiver_address"]
                cus_values['mobile']=order['receiver_mobile']
                cus_values["phone"] = order["receiver_phone"]
                cus_values["openid"] = order["buyer_openid"]
                #销售团队及销售员
                if shop.sale_team:
                    cus_values['section_id']=shop.sale_team.id
                    if shop.sale_team.user_id:
                        cus_values['user_id']=shop.sale_team.user_id.id

                param_value={}
                param_value['official_account']=wxOfficeAccountInfo
                param_value['company_id']=company_id
                result_customer = self.create_customer(env,cus_values,param_value)

                #product_id: oe
                product_sku = order["product_sku"]
                product_id=False
                for product in product_products:
                    if len(product_sku) == 0:
                        product_id = product_products[0].id
                    else:
                        if product_sku.replace('$', '') == product.attribute_value_ids.display_name.replace(' ', ''):
                            product_id = product.id

                #价格由分转变为元
                unit_price=order['product_price']*0.01
                product_num=order['product_count']
                order_create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order["order_create_time"]))

                #notice: order_value:后续单据所需数据
                order_value={}
                order_value.update({
                    'delivery_type':'express',
                    'partner_id':result_customer["customer_id"],
                    'partner_invoice_id':result_customer["contact_id"],
                    'partner_shipping_id':result_customer["contact_id"],
                    'wx_customer_id':result_customer["wx_customer_id"],
                    'data_order':datetime.datetime.now(),
                    'order_policy':'manual',
                    'product_price':unit_price,
                    'order_total_price':unit_price * product_num,
                    'pricelist_id':pricelist_id,
                    'product_id':product_id,
                    'product_count':product_num,
                    'officialaccount_id': wxOfficeAccountInfo.id,
                    'trans_id':order['trans_id'],
                    'order_create_time':order_create_time

                })
                if company_id:
                    order_value.update({'company_id': company_id,})

                #notice: order,小店订单所需数据
                order.update({
                                'product_price':unit_price,
                                'order_total_price':unit_price * product_num,
                                'order_status':str(order["order_status"]),
                                'is_micro_channel_ship':True,
                                'wx_shop':shop.id,
                                'order_create_time':order_create_time
                            })
                print result_customer['customer_id']
                result = self._create_after_order(env,order_value, shop['id'])
                return result['so_obj']
        else:
            raise "获取商品信息错误:" + str(result['errcode']) + result['errmsg']

    # 两个时间字符串相差的天数
    def datediff(self, beginDate, endDate):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        start_t = time.strptime(beginDate, datetime_format)
        end_t = time.strptime(endDate, datetime_format)
        start_active_time = datetime.datetime(*start_t[:6])
        end_active_time = datetime.datetime(*end_t[:6])
        count_days = (end_active_time - start_active_time).days
        return count_days

    def create_customer(self,env, cus_value, param_value):
        '''
        功能：处理OE客户、微信客户、OE客户与微信客户的交叉关系
        :param env:
        :param cus_value:
        :param param_value:
        :return:
        '''
        openid=cus_value.get("openid",False)
        official_account=param_value.get('official_account',False)
        company_id=param_value.get('company_id',False)
        login=param_value.get('login',False)
        result_customer = {}
        # ***************************1.begin 处理收获人***********************************
        # 获取收获人基本信息
        anonymous='匿名用户－%s' % str(int(time.time()))
        name=cus_value.get("name",False)
        if not name:
            cus_value['name']=anonymous
        province = cus_value.get("province",'')
        _province = cus_value.get("province",False)
        if not _province:
            province='qazwsx'
        receiver_value = cus_value
        country_id = '1'  # default
        province_id = False
        # province = cus_value.get("province",'')

        sql_str = "select country_id,id as province_id from res_country_state where name  like " + "'" + province + "%'"
        self._cr.execute(sql_str)
        res = self._cr.fetchall()
        cus_value_update={}
        if len(res) > 0:
            country_id = res[0][0]
            province_id = res[0][1]
            cus_value_update['state_id']=province_id
            cus_value_update['country_id']=country_id
        if company_id:
            cus_value_update['company_id']=company_id

        #$$$头像及性别特殊处理（因客户有可能是收获人，没有这些信息）
        #处理客户头像
        headimgurl = cus_value.get('headimgurl',False)
        if headimgurl:
            image = urllib2.urlopen(headimgurl).read()
            headimg=base64.b64encode(image)
            cus_value_update['image']=headimg

        #性别处理
        sex=cus_value.get('sex',False)
        if sex==1:
            cus_value_update['title']=5
        if sex==2:
            cus_value_update['title']=3

        cus_value.update(cus_value_update)
        cus_instance = env['res.partner']
        oe_customer = False
        oe_contact = False
        unionid=cus_value.get('unionid',False)

        if login:
            user_instance = env['res.users']
            user_s=user_instance.search([('login','=',login)])
            cus_objs = cus_instance.search([('id','=',user_s[0].partner_id.id)])
        else:
            if not unionid:
                cus_objs = cus_instance.search(
                    [('customer', '=', True), ('is_company', '=', False), ('mobile', '=', cus_value.get("mobile",''))])
            else:
                cus_objs = cus_instance.search(['|', ('wx_openid', '=', unionid), ('wx_openid', '=', openid)])
                cus_value['wx_openid']=unionid

        if len(cus_objs) == 0:
            cus_value.update({'customer':True,'is_company':False,'parent_id':False})
            _logger.info('创建客户参数:%s' % cus_value)
            oe_customer = cus_instance.create(cus_value)
        else:
            oe_customer = cus_objs[0]
            if login:
                oe_customer.write(cus_value)
            address = cus_value['street']
            if not (oe_customer.city == cus_value["city"] and oe_customer.street == address):
                # 地址不同，创建该客户的联系人
                cus_value.update({'customer':True,'is_company':False,'parent_id':oe_customer.id})
                contact_objs = cus_instance.search(
                    [('customer', '=', True), ('is_company', '=', False), ('mobile', '=', cus_value.get("mobile",False)),
                     ('city', '=', cus_value.get("city",False)), ('street', '=', address),('parent_id','=',oe_customer.id)])
                if len(contact_objs)==0:
                    oe_contact = cus_instance.sudo().create(cus_value)
                else:
                    oe_contact=contact_objs[0]

        # ***************************1.end处理收获人***********************************
        if not oe_contact:
            pass
        # ***************************2.begin 创建及更新微信客户***********************************
        # 创建及更新微信客户
        import ycloud_wx_customer as wx_customer
        wx_customer_4subscribe = wx_customer.wx_customer_4subscribe(self._cr, self._uid, self._context)
        values = {}
        values['openid'] = openid
        values['officialaccount_id'] = official_account.wx_official_account_id
        wx_customer_id = wx_customer_4subscribe.create_wx_customer(values)
        # ***************************2.end 创建及更新微信客户"***********************************

        # ***************************3.begin （OE客户、微信客户）"***********************************
        ids=oe_customer.wx_customer_ids.ids
        if wx_customer_id.id not in ids:
            ids.append(wx_customer_id.id)
        wx_customer_ids = [[6, False, ids]]
        customer_value = {"wx_customer_ids": wx_customer_ids}
        admin_id=1
        admin_env = Environment(self._cr, admin_id, http.request.context)
        admin_env['res.partner'].search([('id','=',oe_customer.id)]).write(customer_value)
        # ***************************3.end（OE客户、微信客户）"***********************************

        result_customer["customer_id"] = oe_customer.id
        result_customer["cus_obj"] = oe_customer
        result_customer['wx_customer_id']=False
        wx_customer_instance=env['wx.customer']
        wx_customer_objs=wx_customer_instance.search([('openid','=',openid)])
        if len(wx_customer_objs)>0:
            wx_customer_obj=wx_customer_objs[0]
            result_customer['wx_customer_id']=wx_customer_obj.id
            result_customer['wx_customer_obj']=wx_customer_obj
        if oe_contact:
            result_customer["contact_id"] = oe_contact.id
        else:
            result_customer["contact_id"] = oe_customer.id
        _logger.info('create_customer返回值：%s' % str(result_customer))
        return result_customer

    def _create_after_order(self,env, order_value,record_value):
        '''
        功能：处理后续单据：销售订单、客户发票、客户付款单、微信对账单
        :param env:
        :param order_value:
        :param shopid:
        :return:
        '''
        try:
            wx_record_instance = env['wx.shop.order']
            wx_record = wx_record_instance.search_read([('order_id', '=', record_value["order_id"])])
            result={}
            result_mark = "Success"
            so_obj = False
            if len(wx_record) == 0:
                # *************1.创建报价单、订单确认（此时生成销售订单）************************
                so_obj = self._create_sales_order(env,order_value)

                # *************2.创建微信小店订单************************
                record_value["oe_salesorder"] = so_obj.id
                wx_record_obj = wx_record_instance.create(record_value)
                if wx_record_obj:
                    _logger.info('小店订单创建成功')
                else:
                    _logger.info('小店订单创建失败')
                #扣减微信商品中的“微信库存数量”
                product_id = record_value['product_id']
                product_sku = record_value['product_sku']
                wx_product_obj = env['ycloud.wx.product']
                wx_product = wx_product_obj.search([('wx_productid', '=', product_id)])
                if wx_product:
                    if len(product_sku) == 0:
                        wx_product.single_spec_quantity -= 1
                    else:
                        wx_product_line_obj = env['wx.product.line']
                        wx_product_lines = wx_product_line_obj.search([('wx_product_id', '=', wx_product.id)])
                        for wx_product_line in wx_product_lines:
                            if product_sku == "$" + wx_product_line.spec_name + ":$" + wx_product_line.spec_value:
                                wx_product_line.wx_quantity -= 1

                # *************3.生成客户发票及发票确认************************
                invoice_value={}
                invoice_value['so_obj']=so_obj
                account_invoice_obj=self._create_account_invoice(env,invoice_value)

                # *************4.创建客户付款单、登记付款************************
                voucher_value={}
                voucher_value['so_obj']=so_obj
                voucher_value['account_invoice_obj']=account_invoice_obj
                voucher_value['total_fee']=order_value['order_total_price']
                voucher_value['trans_id']=order_value['trans_id']
                account_voucher_obj=self._create_account_voucher(env,voucher_value)

                # *************4.创建微信对账单************************
                bill_value={}
                bill_value['account_voucher_obj']=account_voucher_obj
                bill_value['tradetime']=order_value["order_create_time"]
                bill_value['totalmoney']=order_value["order_total_price"]
                bill_value['wxorder']=order_value['trans_id']
                bill_value['officialaccount_id']=order_value['officialaccount_id']
                self._create_wx_bill(env,bill_value)

            else:
                result_mark = "Already"
            result['result_mark']=result_mark
            result['so_obj']=so_obj
            return result
        except Exception as e:
            _logger.info(e)
            return "Error"

    def _create_sales_order(self, env,order_value):
        '''
        功能：创建销售订单
        :param env:
        :param order_value:
        :return:销售订单对象
        '''
        try:
            partner_id = order_value.get("partner_id",False)
            partner_invoice_id = order_value.get("partner_invoice_id",False)
            partner_shipping_id = order_value.get("partner_shipping_id",False)
            company_id = order_value.get("company_id",False)
            pricelist_id = order_value.get("pricelist_id",False)
            delivery_type=order_value.get("delivery_type",False)
            product_qr_id=order_value.get("product_qr_id",False)

            wx_customer_id = order_value.get("wx_customer_id",False)
            so_instance = env['sale.order']
            so_values = {}
            so_values["delivery_type"] =delivery_type
            so_values["partner_id"] = partner_id
            so_values["partner_invoice_id"] = partner_invoice_id
            so_values["partner_shipping_id"] = partner_shipping_id
            so_values["data_order"] = datetime.datetime.now()
            so_values["pricelist_id"] = pricelist_id
            so_values["order_policy"] = 'manual'  # 从销售订单创建发票草稿
            so_values['wx_customer_id']=wx_customer_id
            if company_id:
                so_values["company_id"] = company_id
            if pricelist_id:
                so_values["pricelist_id"] = pricelist_id  #
            else:
                so_values["pricelist_id"] = 1
            so_values["varehourse_id"] = 1
            pricelist_id = 1
            line_value=[]
            line_values0 = {}
            line_values0['product_id'] = order_value['product_id']
            line_values0['price_unit'] = order_value['product_price']
            line_values0['product_uom_qty'] = order_value['product_count']
            line_value.append([0,False,line_values0])
            if product_qr_id:
                #处理赠品
                gift_product_objs=env['ycloud.gift.product'].search([('product_qr_id','=',product_qr_id)])
                for gift_product_obj in gift_product_objs:
                    gift_product_values={}
                    gift_product_values['product_id'] = gift_product_obj.product_info.id
                    gift_product_values['price_unit'] = 0.00
                    gift_product_values['product_uom_qty'] = gift_product_obj.product_num
                    line_value.append([0,False,gift_product_values])
            so_values['order_line']=line_value
            # ***** 1.创建OE报价单 ********
            so_obj = so_instance.create(so_values)
            # ****** 2.创建OE报价单行 *************
            #self.create_so_line(env,order, so_obj.id)
            # *******3.订单确认（报价单－ >销售订单）***********
            so_obj.action_button_confirm()
            self._cr.commit()
            # self.create_invoice_voucher(so_obj,order)
            return so_obj
        except Exception as e:
            _logger.info(e)
            return False

    def _create_account_invoice(self,env,invoice_value):
        '''
        功能：创建发票、发票确认
        :param env:
        :param invoice_value:
        :return: 客户发票对象
        '''
        so_obj=invoice_value.get('so_obj',False)
        account_invoice_obj=False
        if so_obj:
            # 1.生成草稿发票,查找由销售订单生成的发票
            so_obj.manual_invoice()
            account_invoice_objs = env['account.invoice'].search([('origin', '=', so_obj.name)])
            if len(account_invoice_objs)>0:
                account_invoice_obj=account_invoice_objs[0]
        else:
            account_invoice_obj=env['account.invoice'].create(invoice_value)

        #2.发票－确认生效
        account_invoice_obj.signal_workflow('invoice_open')

        return account_invoice_obj

    def _create_account_voucher(self,env,voucher_value):
        '''
        功能：创建客户付款单、登记付款
        :param env:
        :param voucher_value:
        :return:客户付款单对象
        '''
        so_obj=voucher_value.get('so_obj',False)
        account_invoice_obj=voucher_value.get('account_invoice_obj',False)
        total_fee = voucher_value.get("total_fee",0)
        trans_id=voucher_value.get("trans_id",False)
        company_id=voucher_value.get('company_id',False)
        partner_id=voucher_value.get('partner_id',False)
        order_number=voucher_value.get('order_number',False)
        invoice_title=voucher_value.get('invoice_title',False)
        if so_obj and not company_id:
            company_id = so_obj.company_id.id
        if so_obj and not partner_id:
            partner_id = so_obj.partner_id.id
        if so_obj and not order_number:
            order_number=so_obj.name
        if account_invoice_obj and not invoice_title:
            invoice_title=account_invoice_obj.invoice_title

        id_code=voucher_value.get('id_code',False)
        payment_agreement=voucher_value.get('payment_agreement',False)
        account_voucher_instance = env['account.voucher']
        voucher_name=account_invoice_obj.internal_number

        journals = env['account.journal'].search(
                    [('code', '=', 'Wxpay'), ('company_id', '=', company_id)])
        journal_id = journals and journals[0].id or False
        line_ids = [(6, 0, [])]
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        type = 'receipt'

        # 注意：上下文中应存在发票信息，如果无发票信息，创建的交易分录可能会在其他发票下
        context = {"invoice_id": account_invoice_obj.id, "lang": "zh_CN"}
        vals = account_voucher_instance.with_context(context).onchange_journal(journal_id, line_ids, False,
                                                                                   partner_id, date,
                                                                                   total_fee, type, company_id)
        account_voucher_values = {}
        account_voucher_values['account_id'] = vals['value']['account_id']
        account_voucher_values['amount'] = total_fee
        account_voucher_values['analytic_id'] = False
        account_voucher_values['comment'] = 'Write-Off'
        account_voucher_values['company_id'] = company_id
        account_voucher_values['date'] = date
        account_voucher_values['is_multi_currency'] = False
        account_voucher_values['journal_id'] = journal_id
        account_voucher_values['line_cr_ids'] = [[0, False, val] for val in vals['value']['line_cr_ids']]
        account_voucher_values['line_dr_ids'] = [[0, False, val] for val in vals['value']['line_dr_ids']]
        account_voucher_values['name'] = voucher_name
        account_voucher_values['narration'] = False
        account_voucher_values['partner_id'] = partner_id
        account_voucher_values['payment_option'] = 'without_writeoff'
        account_voucher_values['payment_rate'] = vals['value']['payment_rate']
        account_voucher_values['payment_rate_currency_id'] = vals['value']['payment_rate_currency_id']
        account_voucher_values['period_id'] = vals['value']['period_id']
        account_voucher_values['pre_line'] = True
        if trans_id:
            account_voucher_values['reference']=trans_id
        account_voucher_values['order_number'] = order_number
        account_voucher_values['invoice_title'] = invoice_title
        account_voucher_values['currency_id'] = vals['value']['currency_id']
        account_voucher_values['type'] = type
        account_voucher_values['writeoff_acc_id'] = False
        account_voucher_values['id_code']=id_code
        account_voucher_values['payment_agreement']=payment_agreement

        account_voucher_obj = account_voucher_instance.with_context().create(account_voucher_values)
        account_voucher_obj.button_proforma_voucher()
        return account_voucher_obj

    def _create_wx_bill(self,env,bill_value):
        '''
        功能：创建微信对账单,小店订单通过对账单接口无法获取，再这里处理
        :param env:
        :param bill_value:
        :return:
        '''
        account_voucher_obj=bill_value.get('account_voucher_obj',False)
        tradetime=bill_value.get('tradetime',False)
        totalmoney=bill_value.get('totalmoney',False)
        wxorder=bill_value.get('wxorder',False)
        officialaccount_id=bill_value.get('officialaccount_id',False)
        wx_bill_instance=env['ycloud.wx.bill']
        wx_bill_value={}
        wx_bill_value['tradetime']=tradetime#bill_value["order_create_time"]
        wx_bill_value['wxorder']=wxorder #bill_value['trans_id']
        wx_bill_value['tradetype']='JSAPI'
        wx_bill_value['tradestatus']='SUCCESS'
        wx_bill_value['totalmoney']=totalmoney #bill_value["order_total_price"]
        wx_bill_value['rate']='0.6%'
        wx_bill_value['redpacketmoney']='0'
        wx_bill_value['wxrefund']='0'
        wx_bill_value['refundmoney']='0'
        wx_bill_value['redpacketrefund']='0'
        wx_bill_value['fee']='0.00000'
        wx_bill_value['account_voucher']=account_voucher_obj.number
        wx_bill_value['order_number']=account_voucher_obj.order_number
        wx_bill_value['officialaccount_id']=officialaccount_id
        if account_voucher_obj.payment_agreement:
            wx_bill_value['service_type']='Replace Receive Money'
        else:
            wx_bill_value['service_type']='Main business income'
        wx_bill_value['payment_agreement']=account_voucher_obj.payment_agreement
        wx_bill_objs=wx_bill_instance.search([('wxorder','=',wx_bill_value['wxorder'])])
        if len(wx_bill_objs)==0:
            wx_bill_instance.create(wx_bill_value)

# ************同步微小店订单--end***********************

# ***************************************************#

# #***************** 扩展OE销售订单（sals.order） *******************************
class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def unlink(self):
        '''
        功能：重载销售订单的删除，关联微信订单则不允许
        :return:
        '''
        result_success = ''
        result_error = ''
        for id in self._ids:
            obj = self.browse(id)
            wx_record_ids = self.env['wx.ship.order'].search([('oe_salesorder', '=', id)])
            if len(wx_record_ids) == 0:
                result_success = result_success + obj.name + ','
                super(sale_order, obj).unlink()
                self._cr.commit()
            else:
                result_error = result_error + obj.name + ','
        if result_success != '':
            result_success = "销售订单：%s 删除成功" % result_success[:-1]
        if result_error != '':
            if result_success != '':
                result_error = "\n销售订单：%s 存在关联的微信订单，不允许删除" % result_error[:-1]
            else:
                result_error = "销售订单：%s 存在关联的微信订单，不允许删除" % result_error[:-1]
        msg = "%s%s" % (result_success, result_error)
        if result_error <> '':
            raise except_osv(_('提示'), _(msg))

            # ***************** 扩展OE销售订单（res.partner） *******************************