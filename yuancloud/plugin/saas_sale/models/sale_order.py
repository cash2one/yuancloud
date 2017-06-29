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


class sale_order_extend(models.Model):
    '''
    功能：扩展字段：saas方案
    '''
    _inherit = 'sale.order'

    saas_plan = fields.Many2one('saas_portal.plan', string='产品线')
    order_price = fields.One2many('sale.order.price', 'order_id', string='Price Lines')
    quotation_method = fields.Selection([('project', '按项目报价'), ('service', '按服务报价')], string='报价方式', required=True)
    quotation_header = fields.Char(string='报价单抬头', required=True)

    @api.multi
    def action_generate_saas_product1(self):

        # self.env['product.category'].cate_import([],'zzs')

        spec_info=[{'spec_name':'重量','spec_items':[{'item_name':'50KG','default_code':'ym-6-1','lst_price':60,'qty':300},{'item_name':'100KG','default_code':'ym-6-2','lst_price':85,'qty':850}]}]
        list_value=[{'name':'玉米-6','default_code':'ym-6-1','list_price':70,'qty':300,'thrid_cate_id':10,'image_url':'http://sswy.net/gzl/attachment/jpg/2016/05/284356538239662.jpg','spec_info':spec_info}]
        self.env['product.template'].product_import(list_value,code='zhangzs5',name='test_name6')


    @api.multi
    def action_generate_saas_product(self):
        '''
        功能：按照saas方案展开销售订单行
        :return:
        '''
        try:
            for order in self:
                if not self.saas_plan:
                    _logger.info('没有维护产品线！')
                    raise except_osv(('提示'), ('还未维护产品线，无法创建订单行！'))
                else:
                    _logger.info('销售订单：%s 关联的saas方案=%s' % (order.name, order.saas_plan.name))
                    saas_plan_id = order.saas_plan.id
                    sql_str = '''
                            select product_product_id from saas_portal_module where id in(
                                        select module_id from saas_portal_plan_module where plan_id=%s)
                            ''' % saas_plan_id

                    _logger.info('根据saas.plan获取关联的各module对应产品ID的SQL=%s' % sql_str)
                    self._cr.execute(sql_str)
                    res = self._cr.fetchall()
                    order_line = []
                    for r in res:
                        product_obj = self.env['product.product'].sudo().search([('id', '=', r[0])])
                        product_value = {}
                        product_value['name'] = product_obj.name
                        product_value['product_id'] = product_obj.id
                        product_value['product_uom'] = 1
                        product_value['product_uom_qty'] = 1
                        product_value['price_unit'] = product_obj.list_price
                        product_value['state'] = 'draft'
                        product_value['categ_id'] = product_obj.categ_id.id
                        product_value['must_choose'] = product_obj.must_choose

                        # order.order_line |= order.order_line.new(product_value) #不持久化，先加载到Grid上
                        order_line.append([0, False, product_value])
                    order.write({'order_line': order_line})

        except Exception as e:
            err_msg = '生成订单行异常，%s' % e.message
            err_err = None
            if hasattr(e, 'value'):
                err_err = e.value
            err = err_msg or err_err
            _logger.error(err)
            raise except_osv(('错误'), (err))

    @api.multi
    def print_quotation(self):
        '''
        功能：重写打印按钮，根据是否存在saas方案按不同的模板处理
             打印模板需要的一些订单行及价格子表数据维护
        :return:
        '''
        '''
        :return:
        '''
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})

        #处理订单行，报表需要的数据重新整理
        categ_list = []
        for l in self.order_line:
            if not l.categ_id:
                l.categ_id = l.product_id.categ_id
            categ_id = l.categ_id.id
            if categ_id not in categ_list:
                categ_list.append(categ_id)
        #分类总数
        categ_count = len(categ_list)
        # 每个分类应合并的行数，使用dic ｛分类：模块数量｝
        categ_dic = {}
        categ_dic4price = {}  # 报价所需
        for categ_id in categ_list:
            categ_rowcount = 0
            catet_price = 0
            for l in self.order_line:
                if l.categ_id.id == categ_id:
                    if len(l.product_id.function_ids) == 0 and len(l.product_id.function_product_ids)==0:
                         categ_rowcount += 1
                    else:
                        if len(l.product_id.function_ids) > 0:
                            categ_rowcount += len(l.product_id.function_ids)

                        if len(l.product_id.function_product_ids) > 0:
                            categ_rowcount += len(l.product_id.function_product_ids)

                    catet_price += l.price_unit
            categ_dic[categ_id] = categ_rowcount
            categ_dic4price[categ_id] = catet_price

        # 更新订单行，报表前台使用
        l_categ_id = False
        for l in self.order_line:
            l.categ_count = categ_count
            l.categ_rowcount = categ_dic.get(l.categ_id.id)
            if not l_categ_id:
                l.add_td = True
                l_categ_id = l.categ_id.id
            else:
                if l.categ_id.id == l_categ_id:
                    l.add_td = False
                else:
                    l.add_td = True
                    l_categ_id = l.categ_id.id

        # 处理报价子表,先删除，再创建
        order_prices = self.env['sale.order.price'].search([('order_id', '=', self.id)])
        order_prices.unlink()
        seq = 0
        for categ_id in categ_dic4price:
            order_id = self.id
            seq += 1
            name = self.env['product.category'].search([('id', '=', categ_id)]).name
            price = categ_dic4price.get(categ_id)
            description = ''
            price_value = {}
            price_value['order_id'] = order_id
            price_value['seq'] = seq
            price_value['name'] = name
            if self.quotation_method == 'project':
                price_value['price'] = '%.2f' % (price * 60 / 10000)
            else:
                price_value['price'] = price
            price_value['description'] = description
            self.env['sale.order.price'].create(price_value)

        # 功能清单
        for l in self.order_line:
            order_line_function = self.env['sale.order.line.function'].search([('order_line_id', '=', l.id)])
            order_line_function.unlink()

            for f in l.product_id.function_ids:
                function_value={}
                function_value['order_line_id']=l.id
                function_value['name']=f.name
                function_value['description']=f.description
                self.env['sale.order.line.function'].create(function_value)

            for f in l.product_id.function_product_ids:
                function_value={}
                function_value['order_line_id']=l.id
                function_value['name']=f.name
                function_value['description']=f.description
                self.env['sale.order.line.function'].create(function_value)

            if len(l.product_id.function_product_ids)==0 and len(l.product_id.function_ids)==0:
                function_value={}
                function_value['order_line_id']=l.id
                function_value['name']=l.product_id.name
                function_value['description']=l.product_id.description_sale
                self.env['sale.order.line.function'].create(function_value)


        return self.env['report'].get_action(self, 'saas_sale.report_saleorder')

        # if not self.saas_plan:
        #     return self.env['report'].get_action(self, 'sale.report_saleorder')
        # else:
        #     return self.env['report'].get_action(self, 'saas_sale.report_saleorder')

    @api.onchange('saas_plan')
    def onchange_saas_plan(self):
        self.quotation_header = self.saas_plan.name


class sale_order_line(models.Model):
    '''
    功能：增加产品分类id,用来排序
    '''
    _inherit = 'sale.order.line'
    # saas报价单使用
    categ_id = fields.Many2one('product.category', string='产品分类')
    categ_count = fields.Integer(string='分类数')
    categ_rowcount = fields.Integer(string='分类合并行数')
    add_td = fields.Boolean(string='是否增加TD')
    must_choose = fields.Boolean(string='是否必选')
    _order = 'order_id desc,categ_id ,must_choose desc,sequence, id'

class sale_order_price(models.Model):
    '''
    功能：报表报价部分
    '''
    _name = 'sale.order.price'
    order_id = fields.Many2one('sale.order', string='报价单')
    seq = fields.Char(string='序号')
    name = fields.Char(string='名称')
    price = fields.Char(string='报价')
    description = fields.Char(string='备注')

class sale_order_line_extend(models.Model):
    '''
    功能：扩展字段,记录行对应的功能说明
    '''
    _inherit = 'sale.order.line'
    order_line_function=fields.One2many('sale.order.line.function','order_line_id',string='Function Lines')

class sale_order_line_function(models.Model):
    '''
    功能：报表报价部分
    '''
    _name = 'sale.order.line.function'
    order_line_id=fields.Many2one('sale.order.line', string='报价单行')
    name = fields.Char(string='名称')
    description = fields.Char(string='描述')


