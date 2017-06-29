# -*- coding: utf-8 -*-

# from openerp import models, fields, api
try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields, api
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv

from yuancloud.addons.wx_base.sdks.officalaccount_sdk import product_manager,group_manager

import time

#解码错误
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#日志
import logging
_logger = logging.getLogger(__name__)


def _country_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('res.country').search(cr, uid, [('code', '=', 'CN')], context=context)
    if ids:
        # return ids[0]
        return obj.pool.get('res.country').browse(cr, uid, ids[0], context=context)
    return False

class wx_freight(models.Model):
    _name = 'wx.freight'
    _rec_name = 'oe_deliverycarrier'
    oe_deliverycarrier = fields.Many2one("delivery.carrier", "Delivery Carrier")
    wx_shop = fields.Many2one("wx.shop", "Shop")

class wx_product(models.Model):
    '''
    实体：微信商品
    '''
    _inherits = {'product.template': 'oe_product'}
    _name = 'wx.product'
    oe_product = fields.Many2one("product.template", string="商品", required=True, ondelete="restrict")
    wx_shop = fields.Many2one("wx.shop", string="微信小店" ,required=True)
    wx_freight = fields.Many2one("wx.freight", "运费模版")

    wx_productid = fields.Char(readonly=True, string="微信商品ID")
    wx_image_url = fields.Char(readonly=True, string="主图地址")
    wx_productcategory = fields.Many2one('wx.productcategory', string='商品分类', required=True)
    wx_islimited = fields.Boolean(string="限购")
    wx_buylimit = fields.Integer(string="限购数量")
    wx_ishasreceipt = fields.Boolean(string="是否提供发票")
    wx_isunderguaranty = fields.Boolean(string="是否保修")
    wx_isSupportReplace = fields.Boolean(string="是否支持退换货")
    wx_productcountry = fields.Many2one("res.country", string="国家", required=True,
                                        default=lambda self: _country_get(self, self.env.cr, self.env.user.id))
    wx_productprovince = fields.Many2one("res.country.state", string="省份", required=True)
    wx_productcity = fields.Char(string="城市", required=True)
    wx_productaddress = fields.Char(string="详细地址")
    # wx_productstatus = fields.Selection(
    #     [('relased', 'Relased'), ('on-the-shelf', 'On-the-shelf'), ('off-the-shelf', 'Off-the-shelf'),
    #      ('deleted', 'Deleted')], string="Product Status", readonly=True)
    state = fields.Selection([('draft', '草稿'), ('released', '已发布'), ('onsale', '在销售'), ('closed', '关闭')], readonly=True,
                             string="状态", default='draft')
    wx_productdesp = fields.Text("描述")
    wx_product_lines = fields.One2many('wx.product.line', 'wx_product_id', string='商品规格')
    single_spec = fields.Boolean(string='单规格')
    single_spec_quantity = fields.Integer(string='微信库存数量', help='商品为单规格时有效')
    single_spec_quantity_offset = fields.Integer(string='库存偏移量', help='商品为单规格时有效', default=0)
    wx_product_images = fields.One2many('wx.product.images', 'wx_product_id', string='商品图片')
    # wx_group = fields.Many2one('ycloud.wx.productgroup', string='分组')
    wx_group_cross = fields.Many2many('wx.productgroup', 'ycloud_product_group_rel', 'wx_product_id',
                                      'wx_group_id', string="商品分组")
    wx_group = fields.Char(string='当前分组')
    wx_group_officialaccount = fields.Many2one('wx.officialaccount', string='tmp',
                                               related='wx_shop.wx_official_account')
    _order = 'create_date desc'

    @api.onchange('oe_product')
    def oe_product_change(self):
        '''
        功能：商品变化时处理逻辑
        :return:
        '''
        if self.oe_product:
            # 规格
            self.wx_product_lines = False
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.oe_product.id)])
            for product in products:
                if product.attribute_value_ids:
                    self.single_spec = False
                    self.single_spec_quantity = 0
                    for att_value in product.attribute_value_ids:
                        value = {}
                        value['product_product_id'] = product.id
                        value['spec_name'] = att_value.attribute_id.name
                        value['spec_value'] = att_value.name
                        value['wx_lst_price'] = product.lst_price
                        value['wx_quantity'] = product.qty_available
                        if product.qty_available < 0:
                            value['wx_quantity'] = 0
                        # value['sales_range'] = 'online'
                        self.wx_product_lines |= self.wx_product_lines.new(value)
                else:
                    self.single_spec = True
                    self.single_spec_quantity = 0
                    # 分组

        else:
            self.wx_product_lines = False
            self.single_spec_quantity = 0

    def onchange_country(self,cr,uid,ids,country):
        '''
        功能：国家变化时，清空省份
        :param cr:
        :param uid:
        :param ids:
        :param country:
        :return:
        '''
        val = {
            'wx_productprovince': ''
        }
        return {'value': val}

    @api.one
    def single_reload_product_spec(self):
        '''
        功能：单规格商品
        :return:
        '''
        if self.oe_product:
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.oe_product.id)])
            exist_product_ids = []
            for wx_product_line in self.wx_product_lines:
                exist_product_ids.append(wx_product_line.product_product_id)
            for product in products:
                if product.id not in exist_product_ids:
                    if product.attribute_value_ids:
                        for att_value in product.attribute_value_ids:
                            value = {}
                            value['product_product_id'] = product.id
                            value['spec_name'] = att_value.attribute_id.name
                            value['spec_value'] = att_value.name
                            value['wx_lst_price'] = product.lst_price
                            value['wx_quantity'] = 0
                            value['wx_quantity_offset'] = product.qty_available
                            # value['sales_range'] = 'online'
                            self.wx_product_lines |= self.wx_product_lines.new(value)
        else:
            self.wx_product_lines = False
            self.single_spec_quantity = 0

    @api.model
    def create(self, vals):
        if vals['wx_product_lines']:
            vals['single_spec'] = False
        else:
            vals['single_spec'] = True
        return super(wx_product, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'wx_product_lines' in vals:
            if vals['wx_product_lines']:
                vals['single_spec'] = False
            else:
                vals['single_spec'] = True
        return super(wx_product, self).write(vals)

    def draft(self):
        pass

    def released(self):
        '''
        功能：工作流
        :return:
        '''
        if self.state == 'draft':
            self.create_product()
        else:
            self.off_the_shelf()

    def create_product(self, cr, uid, ids, context=None):
        count = len(ids)
        if count == 0:
            print 'count=0'
        else:
            result_success = ""
            result_error = ""
            for id in ids:
                try:
                    wx_product = self.browse(cr, uid, id, context=context)
                    pricelist_id = -1  # 默认无价目表
                    if wx_product.wx_shop.oe_pricelist.id:
                        pricelist_id = wx_product.wx_shop.oe_pricelist.id
                    print pricelist_id
                    official_account = wx_product.wx_shop.wx_official_account
                    appid = official_account.wx_appid
                    appsecret = official_account.wx_appsecret
                    product_help = product_manager.product_manager(appid, appsecret)
                    # 1.上传商品图片
                    img_result = self.upload_images(product_help, wx_product, True)
                    main_img_url = img_result['main_img_url']
                    imglist = img_result['imglist']
                    detaillist = img_result['detaillist']
                    if not main_img_url:
                        raise except_osv(_('错误'), _('没有维护产品主图，不允许发布！'))
                    # 2.创建商品到微信小店
                    categoryid = wx_product.wx_productcategory.wx_productcategory_id  # "537119729"
                    print categoryid
                    isSupportReplace = wx_product.wx_isSupportReplace
                    product_name = wx_product.oe_product.name
                    standard_price = wx_product.oe_product.list_price
                    isUnderGuaranty = wx_product.wx_isunderguaranty

                    # TODO: 商品分类上的属性，非必输项
                    propertylist = []
                    isHasReceipt = wx_product.wx_ishasreceipt
                    # 运费模版，暂时统一
                    delivery_info = {
                        "delivery_type": 0,
                        "template_id": 0,
                        "express":
                            [{
                                "id": 10000027,
                                "price": 0 * 100
                            }
                            ]
                    }

                    buy_limit = wx_product.wx_buylimit

                    # 获取多规格
                    product_tmpl_id = wx_product.oe_product.id
                    # sku_info=[{
                    #      "id":"$重量",
                    #      "vid":["$50克","$100克"]
                    #  },
                    # {"id": "$长度", "vid":["$1米","$2米"]}

                    # ]
                    sku_info = []
                    for att_line in wx_product.oe_product.attribute_line_ids:
                        dic = {}
                        dic["spec_name"] = '$' + att_line.attribute_id.name
                        dic["spec_values"] = ['$' + v.name for v in att_line.value_ids]
                        sku_info.append({"id": dic['spec_name'], 'vid': dic['spec_values']})

                    product_ids = self.pool.get('product.product').search(cr, uid,
                                                                          [('product_tmpl_id', '=', product_tmpl_id)])
                    location_id = wx_product.wx_shop.oe_location.id
                    # context['location'] = location_id
                    # 指定库存库位
                    products = self.pool.get('product.product').browse(cr, uid, product_ids,
                                                                       context={'location': location_id})
                    # sku_list = {
                    #     "sku_id": "$重量:$50克;$长度:1米",
                    #     "price": standard_price,
                    #     "product_code": "testing",
                    #     "icon_url": main_img_url,
                    #     "ori_price": standard_price,
                    #     "quantity": 800
                    # }
                    sku_list = []
                    for product in products:
                        wx_price = False
                        if pricelist_id > 0:
                            wx_price = self.get_wx_price(cr, uid, product.id, pricelist_id, False, context)
                        dic = {}
                        dic['sku_id'] = ''
                        if wx_price:
                            dic['lst_price'] = wx_price
                        else:
                            dic['lst_price'] = product.lst_price
                        #
                        wx_product_line = self.get_wx_product_line(cr, uid, id, product.id, context)
                        if wx_product.single_spec:
                            if wx_product.single_spec_quantity > 0:
                                sku_list.append({
                                    "sku_id": dic["sku_id"],
                                    "price": dic['lst_price'] * 100,
                                    "product_code": str(int(time.time())),
                                    "icon_url": main_img_url,
                                    "ori_price": standard_price * 100,
                                    "quantity": wx_product.single_spec_quantity  # 固定库存量
                                })
                        elif wx_product_line['issuccess']:
                            dic["sku_id"] += '$' + wx_product_line['spec_name'] + ':$' + wx_product_line['spec_value']
                            dic['qty_available'] = wx_product_line['wx_quantity']
                            sku_list.append({
                                "sku_id": dic["sku_id"],
                                "price": dic['lst_price'] * 100,
                                "product_code": str(int(time.time())),
                                "icon_url": main_img_url,
                                "ori_price": wx_product_line['wx_lst_price'] * 100,
                                "quantity": dic['qty_available']
                            })
                            #
                            # !!!!!!!!!!!!!!!!!!

                    isPostFree = 0
                    country = wx_product.wx_productcountry.name
                    province = wx_product.wx_productprovince.name
                    location = {
                        "country": country,
                        "province": province,
                        "city": wx_product.wx_productcity,
                        "address": wx_product.wx_productaddress
                    }
                    if len(sku_list) > 0:  # 固定库存量
                        result = product_help.create_product(categoryid, product_name, main_img_url,
                                                             imglist, detaillist,
                                                             propertylist, buy_limit, sku_info, sku_list, isPostFree,
                                                             isHasReceipt, isUnderGuaranty, isSupportReplace,
                                                             delivery_info, location)
                        print "-->" + str(result)
                        if result['errcode'] == 0:
                            wx_product.wx_productid = result['product_id']
                            wx_product.wx_image_url = main_img_url
                            # ********修改分组商品******
                            group_ids = ''
                            group_help = group_manager.group_manager(appid, appsecret)
                            if wx_product.wx_group_cross:
                                for group in wx_product.wx_group_cross:
                                    group_ids += str(group.wx_group_id) + ','
                                    group_result = group_help.product_mod_group(group.wx_group_id,
                                                                                wx_product.wx_productid, 1)
                                    if group_result["errcode"] == 0:
                                        _logger.info("商品:%s已经成功加入%s分组" % (product_name, group.wx_group_name))
                            wx_product.wx_group = group_ids[:-1]
                            # ********修改分组商品******
                            wx_product.state = 'released'
                            result_success += product_name
                        else:
                            skd_error_msg = "调用微信商品发布接口报错:%s" % result['errmsg']
                            result_error += product_name
                            raise except_osv(_('错误'), _(skd_error_msg))
                    else:
                        msg = "没有满足发布条件的商品，不能进行发布操作！%s" % '\n1.单规格商品，数量必须大于0；\n2.多规格商品，至少有一个规格的数量大于0!'
                        _logger.debug(msg)
                        raise except_osv(_('错误'), _(msg))

                except Exception as e:
                    _logger.error(e)
                    raise e
            result_success = result_success[:-1]
            result_error = result_error[:-1]
            result_msg = ""
            if result_success != "":
                result_msg += "商品:" + result_success + "发布成功"
            if result_error != "":
                result_msg += "商品:" + result_error + "发布失败"
            # raise except_osv(_('提示'), _(result_msg))
            _logger.debug(result_msg)

    def upload_images(self, product_help, wx_product, is_create):
        values = {}
        # 商品图片
        main_url = wx_product.wx_image_url
        imglist = []
        detaillist = []
        for wx_product_image in wx_product.wx_product_images:
            if wx_product_image.sync_upload or is_create:
                im = wx_product_image.image
                im = im.decode('base64')
                wx_img_name = str(int(time.time())) + ".png"
                uploadinfo = product_help.upload_product_image(im, wx_img_name)
                wx_product_image.sync_upload = False
                if not 'errcode' in uploadinfo:
                    image_url = uploadinfo["url"]
                    wx_product_image.image_url = image_url
                    if wx_product_image.image_uses == 'detail_image':
                        _logger.debug(image_url)
                        detail_img = {"img": image_url}
                        detaillist.append(detail_img)
                        detail_txt = {"text": wx_product_image.text}
                        detaillist.append(detail_txt)
                    elif wx_product_image.image_uses == 'other_image':
                        imglist.append(image_url)
                    else:
                        main_url = image_url
                else:
                    _logger.error("上传图片异常")
            else:
                if wx_product_image.image_uses == 'detail_image':
                    if wx_product_image.image_url:
                        detail_img = {"img": wx_product_image.image_url}
                    else:
                        detail_img = {"img": main_url}
                    detaillist.append(detail_img)
                    detail_txt = {"text": wx_product_image.text}
                    detaillist.append(detail_txt)
                elif wx_product_image.image_uses == 'other_image':
                    if wx_product_image.image_url:
                        imglist.append(wx_product_image.image_url)
                    else:
                        imglist.append(main_url)
                else:
                    main_url = wx_product_image.image_url

        # 没有“主图”类型，则上传OE商品主图
        if not main_url:
            if wx_product.oe_product.image:
                # 商品主图
                im = wx_product.oe_product.image
                im = im.decode('base64')
                wx_img_name = str(int(time.time())) + ".png"
                uploadinfo = product_help.upload_product_image(im, wx_img_name)
                # if uploadinfo["errcode"] == 0:
                #     main_url = uploadinfo["image_url"]
                if not 'errcode' in uploadinfo:
                    main_url = uploadinfo["url"]
                    _logger.debug(main_url)
                else:
                    _logger.error("上传图片异常")
        # 如果商品图片中未维护多图以及详情图，则取商品主图
        if len(imglist) == 0:
            imglist.append(main_url)
            imglist.append(main_url)
        if len(detaillist) == 0:
            detail_img = {"img": main_url}
            detaillist.append(detail_img)
            detail_txt = {"text": wx_product.wx_productdesp}
            detaillist.append(detail_txt)

        values['main_img_url'] = main_url
        values['detaillist'] = detaillist
        values['imglist'] = imglist

        return values

    def get_wx_product_line(self, cr, uid, wx_product_id, product_product_id, context):
        values = {}
        values['issuccess'] = False
        wx_product_line_obj = self.pool.get('wx.product.line')
        wx_product_line_ids = wx_product_line_obj.search(cr, uid, [('wx_product_id', '=', wx_product_id),
                                                                   ('product_product_id', '=', product_product_id),
                                                                   ('wx_quantity', '>=', 0)
                                                                   ])
        wx_product_lines = wx_product_line_obj.browse(cr, uid, wx_product_line_ids, context)
        if len(wx_product_lines) > 0:
            wx_product_line = wx_product_lines[0]
            values['id'] = wx_product_line.id
            values['issuccess'] = True
            values['spec_name'] = wx_product_line.spec_name
            values['spec_value'] = wx_product_line.spec_value
            values['wx_quantity'] = wx_product_line.wx_quantity
            values['wx_lst_price'] = wx_product_line.wx_lst_price
            values['wx_quantity_offset'] = wx_product_line.wx_quantity_offset
        return values

    def get_official_account(self, cr, uid, wx_shop_id):
        '''
        功能：通过微小店的ID获取服务号
        :param cr:
        :param uid:
        :param wx_shop_id:
        :return:
        '''
        result = {}
        print "shopid=-->" + str(wx_shop_id)
        wx_shop = self.pool.get('wx.shop').browse(cr, uid, wx_shop_id)
        official_account_id = wx_shop.wx_official_account.wx_official_account_id
        print "official_account_id=-->" + str(official_account_id)
        # 通过服务号ID获取应用ID及应用密钥
        official_accounts = self.pool.get('wx.officialaccount').search_read(cr, uid, [
            ('wx_official_account_id', '=', official_account_id)], offset=0, limit=1)
        if len(official_accounts) == 1:
            appid = official_accounts[0]["wx_appid"]
            appsercret = official_accounts[0]["wx_appsecret"]
            result["appid"] = appid
            result["appsercret"] = appsercret
        return result

    def onsale(self):
        '''
        功能：商品上架
        :return:
        '''
        self.on_the_shelf()

    def on_the_shelf(self, cr, uid, ids, context=None):
        '''
        功能：商品上架核心方法
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        '''
        result_success = ""
        result_error = ""
        for id in ids:
            wx_product = self.browse(cr, uid, id, context=context)
            product_name = wx_product.oe_product.name
            official_account = wx_product.wx_shop.wx_official_account
            appid = official_account.wx_appid
            appsecret = official_account.wx_appsecret
            product_help = product_manager.product_manager(appid, appsecret)
            result = product_help.modify_product_status(wx_product.wx_productid, 1)
            if result['errcode'] == 0:
                # wx_product.wx_productstatus = 'on-the-shelf'
                wx_product.state = 'onsale'
                result_success += product_name
            else:
                skd_error_msg = "调用微信商品上架接口报错:%s" % result['errmsg']
                result_error += product_name
                raise except_osv(_('错误'), _(skd_error_msg))

        result_success = result_success[:-1]
        result_error = result_error[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "商品:'" + result_success + "'上架成功"
        if result_error != "":
            result_msg += "商品:'" + result_error + "'上架失败"
        # raise except_osv(_('提示'), _(result_msg))
        _logger.debug(result_msg)

    def off_the_shelf(self, cr, uid, ids, context=None):
        '''
        功能：商品下架
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        '''
        result_success = ""
        result_error = ""
        for id in ids:
            wx_product = self.browse(cr, uid, id, context=context)
            product_name = wx_product.oe_product.name
            official_account = wx_product.wx_shop.wx_official_account
            appid = official_account.wx_appid
            appsecret = official_account.wx_appsecret
            product_help = product_manager.product_manager(appid, appsecret)
            result = product_help.modify_product_status(wx_product.wx_productid, 0)
            if result['errcode'] == 0:
                # wx_product.wx_productstatus = 'off-the-shelf'
                wx_product.state = 'released'
                result_success += product_name
            else:
                skd_error_msg = "调用微信商品下架接口报错:%s" % result['errmsg']
                result_error += product_name
                raise except_osv(_('错误'), _(skd_error_msg))
        result_success = result_success[:-1]
        result_error = result_error[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "商品:'" + result_success + "'下架成功"
        if result_error != "":
            result_msg += "商品:'" + result_error + "'下架失败"
        # raise except_osv(_('提示'), _(result_msg))
        _logger.debug(result_msg)


    def close(self):
        '''
        功能：工作流－关闭操作
        :return:
        '''
        if self.state == 'draft':
            self.state = 'closed'
        else:
            self.del_product()

    def del_product(self, cr, uid, ids, context=None):
        '''
        功能：删除微信商品
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        '''
        result_success = ""
        result_error = ""
        for id in ids:
            wx_product = self.browse(cr, uid, id, context=context)
            product_name = wx_product.oe_product.name
            official_account = wx_product.wx_shop.wx_official_account
            appid = official_account.wx_appid
            appsecret = official_account.wx_appsecret
            product_help = product_manager.product_manager(appid, appsecret)
            result = product_help.delete_product(wx_product.wx_productid)
            # 删除接口返回值问题，暂时认为微信商品删除成功
            wx_product.state = 'closed'
            result_success += product_name
            # if result['errcode'] == 0:
            #     # wx_product.wx_productstatus = 'deleted'
            #     wx_product.state='closed'
            #     result_success += product_name
            # else:
            #     result_error += product_name
        result_success = result_success[:-1]
        result_error = result_error[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "商品:'" + result_success + "'删除成功"
        if result_error != "":
            result_msg += "商品:'" + result_error + "'删除失败"
        _logger.debug(result_msg)

    def get_wx_price(self, cr, uid, product_id, pricelist_id, partner_id=False, ctx=None):
        '''
        功能：根据价目表获取价格
        :param cr:
        :param uid:
        :param product_id:
        :param pricelist_id:
        :param partner_id:
        :param ctx:
        :return:
        '''
        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                                                             product_id, 1.0, partner_id, ctx)[pricelist_id]
        return price

    # 调整产品价格
    def batch_sync_product(self, cr, uid, ids, context=None):
        '''
        功能:
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        '''
        result_success = ""
        result_error = ""
        for id in ids:
            try:
                wx_product = self.browse(cr, uid, id, context=context)
                if wx_product.state in ('released'):
                    isSuccess = wx_product.sync_product(False)
                    if isSuccess:
                        result_success = result_success + wx_product.oe_product.name + ','
                    else:
                        result_error = result_error + wx_product.oe_product.name + ','
                else:
                    _logger.debug("%s 不是'已发布'状态，不允许同步" % wx_product.name)
            except Exception as e:
                print e
                _logger.error(e)
        result_success = result_success[:-1]
        result_error = result_error[:-1]
        result_msg = ""
        if result_success != "":
            result_msg += "同步成功的商品:" + result_success
        if result_error != "":
            result_msg += "\n同步失败的商品:" + result_error
        _logger.debug(result_msg)
        # 提示
        raise except_osv(_('提示'), _(result_msg))

    # 重载删除方法
    def unlink(self, cr, uid, ids, context=None):
        result_success = ""
        result_error = ""
        for id in ids:
            obj = self.browse(cr, uid, id, context)
            # 微信商品只有在草稿、关闭状态可删除,避免微信产品下架了，但还有待发货订单（同步微信记录时找不到oe产品，导致无法创建销售订单）
            if obj.state == 'released' or obj.state == 'onsale':
                result_error = result_error + obj.name + ','
            else:
                result_success = result_success + obj.name + ','
                super(wx_product, obj).unlink()
                cr.commit()  # 成功的单独提交
        if result_success != "":
            result_success = "删除成功的商品：" + result_success[:-1]
        if result_error != "":
            result_error = "\n不允许删除的商品：" + result_error[:-1]
        msg = "%s%s" % (result_success, result_error)
        if result_error <> '':
            raise except_osv(_('提示'), _(msg))

    # 同步商品
    @api.one
    def single_sync_product(self):
        self.sync_product(True)

    @api.one
    def sync_product(self, single):
        try:
            product_id = self.wx_productid

            wx_product = self
            # 准备调用sdk
            official_account = wx_product.wx_shop.wx_official_account
            appid = official_account.wx_appid
            appsecret = official_account.wx_appsecret
            product_help = product_manager.product_manager(appid, appsecret)

            img_result = self.upload_images(product_help, wx_product, False)
            main_img_url = img_result['main_img_url']
            imglist = img_result['imglist']
            detaillist = img_result['detaillist']

            #
            productinfo = product_help.get_productInfo(product_id)
            # detail_html=productinfo['product_info']['product_base']['detail_html']
            #
            category_id = wx_product.wx_productcategory.wx_productcategory_id  # 微信产品分类
            product_name = wx_product.oe_product.name  # 商品名字不传，调用接口后清空了
            standard_price = wx_product.oe_product.list_price
            isPostFree = 0
            isHasReceipt = 0
            if self.wx_ishasreceipt:
                isHasReceipt = 1
            isUnderGuaranty = 0
            if self.wx_isunderguaranty:
                isUnderGuaranty = 1
            isSupportReplace = 0
            if self.wx_isSupportReplace:
                isSupportReplace = 1
            buy_limit = self.wx_buylimit
            sku_info = []
            for att_line in wx_product.oe_product.attribute_line_ids:
                dic = {}
                dic["spec_name"] = '$' + att_line.attribute_id.name
                dic["spec_values"] = ['$' + v.name for v in att_line.value_ids]
                sku_info.append({"id": dic['spec_name'], 'vid': dic['spec_values']})
            # sku_list
            product_tmpl_id = wx_product.oe_product.id
            location_id = wx_product.wx_shop.oe_location.id
            products = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id)])

            # 指定库存库位
            sku_list = []
            pricelist_id = -1
            if wx_product.wx_shop.oe_pricelist.id:
                pricelist_id = wx_product.wx_shop.oe_pricelist.id
            for product in products:
                wx_price = False
                if pricelist_id > 0:
                    wx_price = self.get_wx_price(product.id, pricelist_id, False)
                dic = {}
                dic['sku_id'] = ''
                if wx_price:
                    dic['lst_price'] = wx_price
                else:
                    dic['lst_price'] = product.lst_price
                #
                wx_product_line = self.get_wx_product_line(wx_product.id, product.id)
                if wx_product.single_spec:
                    if wx_product.single_spec_quantity > 0:
                        sku_list.append({
                            "sku_id": dic["sku_id"],
                            "price": dic['lst_price'] * 100,
                            "product_code": str(int(time.time())),
                            "icon_url": main_img_url,
                            "ori_price": standard_price * 100,
                            "quantity": wx_product.single_spec_quantity  # 固定库存量
                        })
                    # 更新库存
                    modify_stock_qty_result = product_help.modify_stock_qty(product_id, '',
                                                                            wx_product.single_spec_quantity_offset)
                    if modify_stock_qty_result['errcode'] == 0:
                        wx_product.single_spec_quantity += wx_product.single_spec_quantity_offset
                        wx_product.single_spec_quantity_offset = 0
                        _logger.info('产品：%s 更新库存成功' % product_name)
                    else:
                        _logger.info('产品：%s 更新库存失败' % product_name)

                elif wx_product_line['issuccess']:
                    dic["sku_id"] += '$' + wx_product_line['spec_name'] + ':$' + wx_product_line['spec_value']
                    dic['qty_available'] = wx_product_line['wx_quantity']
                    sku_list.append({
                        "sku_id": dic["sku_id"],
                        "price": dic['lst_price'] * 100,
                        "product_code": str(int(time.time())),
                        "icon_url": main_img_url,
                        "ori_price": wx_product_line['wx_lst_price'] * 100,
                        "quantity": dic['qty_available']
                    })
                    # 更新库存
                    stock_qty = wx_product_line["wx_quantity_offset"]
                    if stock_qty <> 0:
                        _logger.info("满足更新库存条件，准备更新库存")
                        stock_skuinfo_id = wx_product_line['spec_name']
                        stock_skuinfo_vid = wx_product_line['spec_value']
                        stock_skuinfo = "$" + stock_skuinfo_id + ":$" + stock_skuinfo_vid
                        modify_stock_qty_result = product_help.modify_stock_qty(product_id, stock_skuinfo, stock_qty)
                        if modify_stock_qty_result['errcode'] == 0:
                            wx_product_line_obj = self.env['ycloud.wx.product.line']
                            wx_product_line4stock = wx_product_line_obj.search([('id', '=', wx_product_line['id'])])
                            wx_product_line4stock.wx_quantity += stock_qty
                            wx_product_line4stock.wx_quantity_offset = 0
                            _logger.info('%s 更新库存成功' % stock_skuinfo)
                        else:
                            _logger.info('%s 更新库存失败' % stock_skuinfo)
                    else:
                        _logger.info("不满足更新库存条件，不处理库存")
            # location
            country = wx_product.wx_productcountry.name
            province = wx_product.wx_productprovince.name
            location = {
                "country": country,
                "province": province,
                "city": wx_product.wx_productcity,
                "address": wx_product.wx_productaddress
            }
            # 运费模版，暂时统一
            delivery_info = {
                "delivery_type": 0,
                "template_id": 0,
                "express":
                    [{
                        "id": 10000027,
                        "price": 0 * 100
                    }
                    ]
            }
            result = product_help.modify_product_info(category_id, product_name, product_id, main_img_url, imglist,
                                                      detaillist, buy_limit,
                                                      sku_info,
                                                      sku_list,
                                                      isPostFree, isHasReceipt, isUnderGuaranty, isSupportReplace,
                                                      delivery_info,
                                                      location)
            isSuccess = False
            if result['errcode'] == 0:
                # ********修改分组商品******
                group_ids = ''
                list_old = wx_product.wx_group.split(',')
                list_new = []
                if wx_product.wx_group_cross:
                    for group in wx_product.wx_group_cross:
                        group_ids += str(group.wx_group_id) + ','
                        list_new.append(str(group.wx_group_id))
                wx_product.wx_group = group_ids[:-1]
                list_group_del = list(set(list_old) - set(list_new))
                list_group_add = list(set(list_new) - set(list_old))

                group_help = group_manager.group_manager(appid, appsecret)
                for group_id in list_group_add:
                    if len(group_id) > 0:
                        group_result = group_help.product_mod_group(int(group_id), wx_product.wx_productid, 1)
                        if group_result["errcode"] == 0:
                            _logger.info("pass")
                        else:
                            _logger.info("error")
                for group_id in list_group_del:
                    if len(group_id) > 0:
                        group_result = group_help.product_mod_group(int(group_id), wx_product.wx_productid, 0)
                        if group_result["errcode"] == 0:
                            _logger.info("pass")
                        else:
                            _logger.info("error")

                # if wx_product.wx_group_cross:
                #     for group in wx_product.wx_group_cross:
                #         group_result = group_help.product_mod_group(group.wx_group_id,wx_product.wx_productid, 1)
                #         if group_result["errcode"] == 0:
                #             _logger.info("商品:%s已经成功加入%s分组" % (product_name, group.wx_group_name))
                # else:
                #     pass
                # ********修改分组商品******

                if single:
                    _logger.info('同步成功')
                    # raise except_osv(_('提示'), _('同步成功!'))
                else:
                    isSuccess = True
            else:
                if single:
                    msg = '同步商品出错，错误原因: %s' % result['errmsg']
                    raise except_osv(_('错误'), _(msg))
                else:
                    pass
            return isSuccess
        except Exception as e:
            _logger.error(e)
            raise e


# #微信商品子表
class wx_product_line(models.Model):
    _name = 'wx.product.line'
    wx_product_id = fields.Many2one('wx.product', '微信商品')
    wx_product_state = fields.Selection(string='微信商品状态', related='wx_product_id.state')
    product_product_id = fields.Integer(string='产品规格ID')
    spec_name = fields.Char(string='规格名称')
    spec_value = fields.Char(string='属性')
    wx_quantity = fields.Integer(string='微信库存量')
    wx_quantity_offset = fields.Integer(string='库存偏移量', default=0)
    wx_lst_price = fields.Float(string='公开价格', digits=(16, 2))
    # sales_range = fields.Selection([('online', '线上'), ('offline', '线下')], string='销售范围')
    _order = 'product_product_id'


class wx_product_image(models.Model):
    _name = 'wx.product.images'
    wx_product_id = fields.Many2one('wx.product', '微信商品')
    image_uses = fields.Selection([('main_image', '主图'), ('other_image', '其它图片'), ('detail_image', '详情图片')],
                                  string='图片用途',
                                  default='detail_image')
    serial_number = fields.Integer(string='序号')
    image = fields.Binary("图片")
    text = fields.Text(string="文字")
    image_url = fields.Char(string='图片地址')
    sync_upload = fields.Boolean(string='同步时需上传', help='同步商品时有效')
    _order = 'serial_number'

class wx_productcategory(models.Model):
    '''
    实体：微信商品分类
    '''
    _name = 'wx.productcategory'
    _rec_name = "wx_productcategory_name"
    wx_productcategory_id = fields.Char("分类ID")
    wx_productcategory_name = fields.Char("分类名称")

# class wx_carrier(models.Model):
#     '''
#     功能：微信承运方
#     '''
#     _inherits = {'delivery.carrier': 'oe_carrier'}
#     _name = 'wx.carrier'
#     oe_carrier = fields.Many2one("delivery.carrier", string="OE承运方", required=True, ondelete="restrict")
#     wx_carrier_code=fields.Char(string="承运方编码")
