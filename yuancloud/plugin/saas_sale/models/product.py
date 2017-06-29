# -*- coding: utf-8 -*-
from yuancloud import models, fields, api
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
_logger = logging.getLogger(__name__)
from lxml import etree
from yuancloud.osv.osv import except_osv
from yuancloud.tools.translate import _

class product_template_functionlist(models.Model):
    '''
    功能：新增产品子表，“功能清单”
    '''
    _name = 'product.template.function'
    #名称，描述，是否必选，标准价格
    name=fields.Char(string='名称')
    description=fields.Text(string='描述')
    must_choose=fields.Boolean(string='是否必选')
    standard_price=fields.Float(digits=(12, 2),string='标准价格')
    product_id=fields.Many2one('product.template',string='商品')

class product_template_extend(models.Model):
    '''
    功能：为产品增加子表:功能清单
    '''
    _inherit = 'product.template'
    must_choose=fields.Boolean(string='必选')
    function_ids=fields.One2many('product.template.function','product_id',string='功能清单')

class product_product_functionlist(models.Model):
    '''
    功能：新增产品子表，“功能清单”
    '''
    _name = 'product.product.function'
    #名称，描述，是否必选，标准价格
    name=fields.Char(string='名称')
    description=fields.Text(string='描述')
    must_choose=fields.Boolean(string='是否必选')
    standard_price=fields.Float(digits=(12, 2),string='标准价格')
    product_id=fields.Many2one('product.product',string='商品')

class product_product_extend(models.Model):
    '''
    功能：为产品增加子表:功能清单
    '''
    _inherit = 'product.product'
    function_product_ids=fields.One2many('product.product.function','product_id',string='规格清单')

