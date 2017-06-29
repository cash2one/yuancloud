# -*- coding: utf-8 -*-

# from openerp import models, fields, api

import itertools
from lxml import etree

from yuancloud import models, fields, api, _

import json

class wx_shop(models.Model):
    '''
    实体：微信小店
    '''
    _name = 'wx.shop'
    _rec_name = 'shop_name'
    shop_category = fields.Selection([('wx', '微信'), ('taobao', '淘宝'), ('jd', '京东'), ('yz', '有赞')], string="店铺分类",
                                     readonly=True, default='wx')
    shop_id = fields.Char(string='店铺标识', required=True)
    shop_name = fields.Char(string='店铺名称', required=True)
    oe_pricelist = fields.Many2one("product.pricelist", "价目表")
    oe_location = fields.Many2one('stock.location', '库存库位', required=True)
    sale_team=fields.Many2one('crm.team', '销售团队')
    return_picking_type=fields.Many2one("stock.picking.type",string="退货分拣类型")
    wx_official_account = fields.Many2one("wx.officialaccount", string="微信服务号", required=True)
