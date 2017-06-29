# -*- coding: utf-8 -*-
from yuancloud import models, fields, api
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
_logger = logging.getLogger(__name__)

class account_account(models.Model):
    '''
    功能：科目增加-“是否预算科目”
    '''
    _inherit ='account.account'
    budget=fields.Boolean(string='是否预算科目')

    @api.model
    def create(self, vals):
        '''
        功能：如果是“预算科目”则创建“预算状况”
        :param vals:
        :return:
        '''
        try:
            account_obj=super(account_account,self).create(vals)
            is_budget=vals.get('budget',False)
            if is_budget:
                _logger.info('预算科目，准备创建预算状况、产品...')
                self._create_budget_pos(account_obj.id,account_obj.name)
                self._create_product(account_obj.id,account_obj.name,account_obj.company_id.id)
            return account_obj
        except Exception as e:
            err_msg='新增科目出现异常，异常信息:%s' % e.message
            _logger.error(err_msg)
            raise e

    @api.multi
    def write(self, vals):
        '''
        功能：由“非预算科目”更改为“预算科目时”处理预算状况
        :param vals:
        :return:
        '''
        try:
            is_budget=vals.get('budget',False)
            if is_budget:
                _logger.info('预算科目，准备创建预算状况、产品...')
                self._create_budget_pos(self.id,self.name)
                self._create_product(self.id,self.name,self.company_id.id)
            else:
                _logger.info('非预算科目，不做处理...')
            return super(account_account,self).write(vals)

        except Exception as e:
            err_msg='更新科目出现异常，异常信息:%s' % e.message
            _logger.error(err_msg)
            raise e

    def _create_budget_pos(self,account_id,account_name):
        '''
        功能：根据“科目”创建“预算状况”
        :return:
        '''
        try:
            _logger.info('_create_budget_pos 接收到的参数：account_id=%s,account_name=%s' % (account_id,account_name))
            budget_post_instance=self.env['account.budget.post']
            budget_post_objs=budget_post_instance.search([('name','=',account_name)])
            if len(budget_post_objs)==0:
                budget_post_value={}
                budget_post_value['name']=account_name
                budget_post_value['account_ids']=[[6,False,[account_id]]]
                budget_post_instance.create(budget_post_value)
            else:
                _logger.info('对应科目%s的预算状况已存在' % account_name)

        except Exception as e:
            err_msg='根据科目创建预算状况时出现异常：%s' % e.message
            _logger.error(err_msg)

    def _create_product(self,account_id,account_name,company_id):
        '''
        功能：创建产品
        :return:
        '''
        try:

            _logger.info('_create_product 接收到的参数：account_id=%s,account_name=%s,company_id=%s' % (account_id,account_name,company_id))
            product_product_instance=self.env['product.product']
            product_product_instance_objs=product_product_instance.search([('name','=',account_name)])
            if len(product_product_instance_objs)==0:
                product_product_value={}
                product_product_value['name']=account_name
                product_product_value['sale_ok']=False
                product_product_value['can_be_expensed']=True
                product_product_value['property_account_expense_id']=account_id
                product_product_value['company_id']=company_id
                product_product_value['taxes_id']=False
                product_product_value['supplier_taxes_id']=False
                product_product_instance.create(product_product_value)
            else:
                _logger.info('对应科目%s的产品已存在' % account_name)

        except Exception as e:
            err_msg='根据科目创建产品时出现异常：%s' % e.message
            _logger.error(err_msg)
