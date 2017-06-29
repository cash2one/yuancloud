# -*- coding: utf-8 -*-
import itertools
from lxml import etree
import urllib2
import base64
from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
import datetime
import logging

_logger = logging.getLogger(__name__)

class product(models.Model):
    '''
    产品实体：
    '''
    _inherit = 'product.template'

    @api.model
    def product_import(self,list_value,**kwargs):
        '''
        功能：产品导入
        '''
        try:
            source_code=kwargs['code']
            source_name=kwargs['name']
            location_id=self.env['stock.location']._location(**kwargs)
            for vals in list_value:
                default_code=vals['default_code']
                multy_spec=vals['spec_info']!=None and len(vals['spec_info'])>0
                exist_products=self.env['product.template'].search([('default_code','=',default_code)])
                if multy_spec:
                    spec_result=self._get_spec_value(vals['spec_info'])
                    attribute_line_ids=spec_result['attribute_line_ids']
                    product_infos=spec_result['product_infos']
                    vals['attribute_line_ids']=attribute_line_ids

                vals['sale_ok']=True  #可销售
                vals['purchase_ok']=True #可采购
                vals['type']='product' #库存商品
                vals['active']=True #
                vals['available_in_pos']=True #
                vals['categ_id']=self._get_category_id(vals.get('third_cate_id',False)) #内部分类
                vals['company_id']=1 #公司
                vals['invoice_policy']='order' #发票开具策略
                vals['purchase_method']='receive' # 控制采购订单
                vals['uom_id']=1
                imgurl = vals.get('image_url',False) #图片地址
                if imgurl:
                    image = urllib2.urlopen(imgurl).read()
                    product_image=base64.b64encode(image)
                    vals['image']=product_image

                product_template_id=None
                if len(exist_products)==0:
                    #不存在此编码的产品，进行新增操作
                    product_template_id=self.env['product.template'].create(vals)
                    # self._cr.commit()
                else:
                    #存在此编码的商品，进行修改操作
                    product_template_id=exist_products[0]
                    update_value={}
                    update_value['name']=vals['name']
                    update_value['categ_id']=vals['categ_id']
                    update_value['image']=vals.get('image',False)
                    update_value['spec_info']=vals.get('spec_info',False)
                    update_value['list_price']=vals['list_price']
                    exist_products[0].write(update_value)

                #处理规格产品属性,商品编号、价格、库存
                kv={'product_tmpl_id':product_template_id.id,'location_id':location_id}
                if multy_spec:
                    kv['product_infos']=product_infos
                else:
                    kv['stock_qty']=vals['qty']
                self._modify_product(**kv)

        except Exception as e:
            _logger.error(e)
            raise e

    def _get_spec_value(self,spec_info):
        #处理多规格
        for spec in spec_info:
            spec_values={}
            spec_name=spec['spec_name'] #规格
            spec_values['name']=spec_name
            spec_values['type']='radio'
            exit_attribute=self.env['product.attribute'].search([('name','=',spec_name)])
            attribute_id=-1
            if len(exit_attribute)>0:
                attribute_id=exit_attribute[0].id
            else:
                attribute_id=self.env['product.attribute'].create(spec_values).id

            value_ids=[]
            product_infos=[]
            for spec_item in spec['spec_items']:
                item_name=spec_item['item_name']
                exist_item=self.env['product.attribute.value'].search([('name','=',item_name)])
                att_id=-1
                if len(exist_item)==0:
                    spec_item_Value={}
                    spec_item_Value['name']=spec_item['item_name']
                    spec_item_Value['attribute_id']=attribute_id
                    att_id=self.env['product.attribute.value'].create(spec_item_Value).id
                else:
                    att_id=exist_item[0].id
                value_ids.append(att_id)
                product_infos.append({'att_id':att_id,'default_code':spec_item['default_code'],'lst_price':spec_item['lst_price'],'qty':spec_item['qty']})

            attribute_line_ids=[[0, False, {u'attribute_id': attribute_id, u'value_ids': [[6, False, value_ids]]}]]
            result={'attribute_line_ids':attribute_line_ids,'product_infos':product_infos}

        return result

    def _modify_product(self,**kwargs):
        '''
        功能：处理规格产品
        :param product_tmpl_id:
        :param product_infos:
        :return:
        '''
        product_tmpl_id=kwargs['product_tmpl_id']
        product_infos=[]
        stock_qty=1
        if kwargs.has_key('product_infos'):
            product_infos=kwargs['product_infos']
        if kwargs.has_key('stock_qty'):
            stock_qty=kwargs['stock_qty']

        location_id=kwargs['location_id']
        product_product_obj=self.env['product.product']
        spec_products=product_product_obj.search([('product_tmpl_id','=',product_tmpl_id)])
        spec_product_ids=[]
        for spec_product in spec_products:
            spec_product_ids.append(str(spec_product.id))
            if len(product_infos)==0:
                #单规格产品，维护在手量
                spec_product.qty_available=stock_qty
                kv={}
                kv['location_id']=location_id
                kv['product_id']=spec_product.id
                kv['product_tmpl_id']=product_tmpl_id
                kv['new_quantity']=stock_qty
                kv['spec_count']=len(spec_products)
                self._process_stock_qty(**kv)

        product_template_instance=self.env['product.template'].search([('id','=',product_tmpl_id)])
        if len(product_infos)>0:
            lst_price=100000000.00 #1个亿 标准价
            for product_info in product_infos:
                if lst_price > product_info['lst_price'] :
                    lst_price = product_info['lst_price']
            if product_template_instance:
                product_template_instance.list_price=lst_price

            for product_info in product_infos:
                att_id=product_info['att_id']
                #1.处理规格产品的商品编号
                sql_str = '''select prod_id from product_attribute_value_product_product_rel as rel
                          where rel.att_id=%s and prod_id in (%s)
                          ''' % (att_id,','.join(spec_product_ids))

                _logger.info('根据规格ID，查找具体规格产品=%s' % sql_str)
                self._cr.execute(sql_str)
                res = self._cr.fetchall()
                for r in res:
                    product_id=r[0]
                    product = product_product_obj.search([('id','=',product_id)])
                    product.default_code=product_info['default_code']
                    product.qty_available=product_info['qty']
                    #多规格产品，维护在手量
                    kv={}
                    kv['location_id']=location_id
                    kv['product_id']=product_id
                    kv['product_tmpl_id']=product_tmpl_id
                    kv['new_quantity']=product_info['qty']
                    kv['spec_count']=len(product_infos)
                    self._process_stock_qty(**kv)

                #2.处理规格产品价格差异
                attribute_value_obj=self.env['product.attribute.price']
                attribute_value_instance=attribute_value_obj.search([('value_id','=',att_id),('product_tmpl_id','=',product_tmpl_id)])
                if attribute_value_instance:
                    attribute_value_instance.price_extra=product_info['lst_price']-lst_price
                else:
                    v={'value_id':att_id,'product_tmpl_id':product_tmpl_id,'price_extra':product_info['lst_price']-lst_price}
                    attribute_value_obj.create(v)


    def _get_category_id(self,third_id):
        '''
        根据第三方分类id获取yuancloud产品内部分类id
        :param third_id:
        :return:
        '''
        p_categorys=self.env['product.category'].search([('third_id','=',third_id)])
        if len(p_categorys)>0:
            return p_categorys[0].id
        else:
            return 1

    def _process_stock_qty(self,**kwargs):
        #处理库存
        location_id=kwargs['location_id']
        product_id=kwargs['product_id']
        product_tmpl_id=kwargs['product_tmpl_id']
        new_quantity=kwargs['new_quantity']
        spec_count=kwargs['spec_count']
        stock_value={}
        stock_value['location_id']=location_id
        stock_value['product_id']=product_id
        stock_value['product_tmpl_id']=product_tmpl_id
        stock_value['product_variant_count']=spec_count
        stock_value['new_quantity']=new_quantity
        stock_context= {
             'active_id':product_tmpl_id
            ,'active_ids':[product_tmpl_id]
            ,'active_model':'product.template'
            ,'lang':'zh_CN'
            ,'params':{'action':126}
            ,'search_disable_customer_filters':True
            ,'tz':False
            ,'uid':self._uid
        }
        stock_change_id=self.env['stock.change.product.qty'].with_context(
           stock_context
        ).create(stock_value).id
        self.pool.get('stock.change.product.qty').change_product_qty(self._cr,self._uid,[stock_change_id],context=stock_context)

class product_cate(models.Model):
    '''
    产品内部分类：
    '''
    _inherit = 'product.category'
    third_id=fields.Integer(string='第三方分类ID')

    @api.model
    def cate_import(self,list_value):
        '''
        功能：导入第三方系统的产品分类
        :param list_value:
        :param source_code: 第三方编码，可以是数据库名称
        :return:
        '''
        list_sort=sorted(list_value,key=lambda k:k["parent_id"])
        for vals in list_sort:
            cate_value={}
            cate_value['third_id']=vals['third_id']
            cate_value['name']=vals['name']
            p_category_obj=self.env['product.category']
            parent_id=vals['parent_id']
            exist_category=p_category_obj.search([('third_id','=',vals['third_id'])])
            if len(exist_category)==0:
                if int(parent_id)!=0:
                    exist_parent_category=p_category_obj.search([('third_id','=',parent_id)])
                    if len(exist_parent_category)>0:
                        cate_value['parent_id']=exist_parent_category[0].id
                p_category_obj.create(cate_value)

            else:
                exist_category.write(cate_value)









