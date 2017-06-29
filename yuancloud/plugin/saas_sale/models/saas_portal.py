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


class saas_portal_module_extend(models.Model):
    '''
    功能：扩展字段：商品、指导价
    '''
    _inherit ='saas_portal.module'

    product_product_id=fields.Many2one('product.product',string='商品')
    guide_price=fields.Float(digits=(12, 2),string='指导价',required=True) #指导价必须输入
    category_name=fields.Char(string='所属分类') # 模块分类
    must_choose=fields.Boolean(string='是否必选')

    @api.model
    def create(self, vals):
        '''
        功能：重写create,如果产品空，依据模块信息创建对应商品
        :param vals:
        :return:
        '''
        try:
            _logger.info('saas_portal.module开始新增保存操作...')
            if not vals['product_product_id']:
                _logger.info('商品为空，根据模块信息创建商品...')
                product_name=vals['name'] #module的名称为商品名
                product_product_instance=self.env['product.product']
                product_product_objs=product_product_instance.search([('name','=',product_name)])
                product_product_obj=False
                if len(product_product_objs)==0:
                    _logger.info('新增可销售的服务类产品%s' % product_name)
                    product_product_value={}
                    product_product_value['name']=product_name
                    product_product_value['sale_ok']=True #可销售
                    product_product_value['type']='service' #产品类型为：服务
                    # product_product_value['property_account_expense_id']=account_id
                    # product_product_value['company_id']=company_id
                    product_product_value['list_price']=vals['guide_price']
                    product_product_value['taxes_id']=False
                    product_product_value['supplier_taxes_id']=False
                    product_product_value['must_choose']=vals.get('must_choose',False)
                    product_product_value['categ_id']=self._get_category(vals.get('category_name','基础')) #没有维护分类，默认“基础”
                    product_product_value['description_sale']=vals.get('summary',product_name)
                    product_product_obj=product_product_instance.create(product_product_value)
                else:
                    _logger.info('名称=%s的商品已存在，获取它' % product_name)
                    product_product_obj=product_product_objs[0]
                vals['product_product_id']=product_product_obj.id

            return super(saas_portal_module_extend,self).create(vals)
        except Exception as e:
            err_msg='新增saas_portal.module异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise e
    def _get_category(self,category_name):
        '''
        功能：通过名字获取产品分类ＩＤ
        :param category_name:
        :return:
        '''
        product_category_s=self.env['product.category'].search([('name','=',category_name)])
        if len(product_category_s)==0:
            return self.env['product.category'].create({'name':category_name}).id
        else:
            return product_category_s[0].id

    @api.multi
    def write(self, vals):
        '''
        功能：重写write,如果产品空，依据模块信息创建对应商品
        :param vals:
        :return:
        '''
        try:
            for portal_module in self:
                _logger.info('saas_portal.module开始更新保存操作...')
                exist_product=vals.get('product_product_id',False)
                if not exist_product:
                    _logger.info('商品为空，根据模块信息创建商品...')
                    product_name=portal_module.name #module的名称为商品名
                    product_product_instance=self.env['product.product']
                    product_product_objs=product_product_instance.search([('name','=',product_name)])
                    product_product_obj=False
                    if len(product_product_objs)==0:
                        _logger.info('新增可销售的服务类产品%s' % product_name)
                        product_product_value={}
                        product_product_value['name']=product_name
                        product_product_value['sale_ok']=True #可销售
                        product_product_value['type']='service' #产品类型为：服务
                        # product_product_value['property_account_expense_id']=account_id
                        # product_product_value['company_id']=company_id
                        product_product_value['list_price']=vals.get('guide_price',0.0)
                        product_product_value['taxes_id']=False
                        product_product_value['supplier_taxes_id']=False
                        product_product_value['description_sale']=vals.get('summary',product_name)
                        product_product_obj=product_product_instance.create(product_product_value)
                    else:
                        _logger.info('名称=%s的商品已存在，获取它' % product_name)
                        product_product_obj=product_product_objs[0]
                    vals['product_product_id']=product_product_obj.id
                super(saas_portal_module_extend,self).write(vals)
                return True
        except Exception as e:
            err_msg='更新saas_portal.module异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise e

    @api.onchange('module_id')
    def onchange_module_id(self):
        if self.module_id:
            self.name = self.module_id.shortdesc
            self.technical_name = self.module_id.name
            self.summary = self.module_id.summary
            self.author = self.module_id.author
            self.url = self.module_id.url

            #产品分类处理，翻译问题
            category_dic={}
            category_dic['Finance Management']='财务管理系统'
            category_dic['Content Management']='内容管理系统'
            category_dic['Manufacturing']='生产管理系统'
            category_dic['Office Automation']='办公自动化系统'
            category_dic['Offline 2 Online']='O2O'
            category_dic['Product Lifecycle Management']='PLM系统'
            category_dic['Wechat']='微信管理系统'
            category_dic['yuancloud Education']='教育管理系统'
            category_dic[u'人力资源']='人力资源管理系统'
            category_dic[u'库存管理']='库存管理系统'
            category_dic[u'采购']='采购管理系统'
            category_dic[u'销售']='销售管理系统'
            category_dic[u'零售']='零售管理系统'
            category_dic[u'知识管理']='知识管理系统'

            category_key=self.module_id.category_id.name
            category_name=category_dic.get(category_key)
            if not category_name:
                category_name=category_key
            self.category_name=category_name

        else:
            self.name, self.technical_name, self.summary, self.author, self.url  = [False] * 5


