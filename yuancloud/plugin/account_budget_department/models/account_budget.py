# -*- coding: utf-8 -*-
from yuancloud import models, fields, api
from yuancloud.osv import fields, osv
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
_logger = logging.getLogger(__name__)

from dateutil import rrule
import datetime
import calendar
import math

class crossovered_budget(osv.osv):
    '''
    功能：预算增加-部门,科目，金额
    '''
    _inherit ='crossovered.budget'

    def _get_month_number(self,str_start_date,str_end_date):
        strptime_start=time.strptime(str_start_date,"%Y-%m-%d")
        strptime_end=time.strptime(str_end_date,"%Y-%m-%d")
        start_date=datetime.date(strptime_start.tm_year,strptime_start.tm_mon,strptime_start.tm_mday)
        end_date=datetime.date(strptime_end.tm_year,strptime_end.tm_mon,strptime_end.tm_mday)
        month_count=rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date).count()
        return month_count

    def _get_month_avera_amount(self, cr, uid, ids, name, args, context=None):
        '''
        功能：计算月平均预算额度
        :param cr:
        :param uid:
        :param ids:
        :param name:
        :param args:
        :param context:
        :return:
        '''
        res={}
        for budget in self.browse(cr, uid, ids, context=context):
            str_start_date=budget.date_from
            str_end_date=budget.date_to
            month_count=self._get_month_number(str_start_date,str_end_date)
            res[budget.id]=round(budget.total_amount/month_count,2)
        return res


    def _get_quarter_avera_amount(self, cr, uid, ids, name, args, context=None):
        '''
        功能：计算季度平均预算额度
        :param cr:
        :param uid:
        :param ids:
        :param name:
        :param args:
        :param context:
        :return:
        '''
        res={}
        for budget in self.browse(cr, uid, ids, context=context):
            str_start_date=budget.date_from
            str_end_date=budget.date_to
            month_count=self._get_month_number(str_start_date,str_end_date)
            res[budget.id]=round(budget.total_amount/month_count,2) * 3
        return res

    _columns = {
        'department_id':fields.many2one('hr.department',string='部门'),
        'account_id':fields.many2one('account.account',string='预算科目'),
        'total_amount':fields.float(digits=(12, 2), string='预算总金额', required=True),
        'month_avera_amount':fields.function(_get_month_avera_amount, string='月均预算额', type='float', digits=(12, 2)),
        'quarter_avera_amount':fields.function(_get_quarter_avera_amount, string='季均预算额', type='float', digits=(12, 2)),
    }
    # department_id=fields.Many2one('hr.department',string='部门')
    # account_id=fields.Many2one('account.account',string='预算科目')
    # total_amount=fields.Float(digits=(12, 2), string='预算总金额', required=True)
    _defaults = {
                'date_from':time.strftime('%Y-01-01',time.localtime(time.time())),
                'date_to':time.strftime('%Y-12-31',time.localtime(time.time()))
            }
    @api.model
    def create(self, vals):
        '''
        功能：重写“预算”的新增方法，
        :param vals:
        :return:
        '''
        try:
            department=self.env['hr.department'].search([('id','=',vals.get('department_id',0))])
            account=self.env['account.account'].search([('id','=',vals.get('account_id',0))])
            if department and account:
                #***********分析账号******************#
                _logger.info('部门及科目都不为空，处理分析账号...')
                analytic_accout_name='%s-%s' % (department.name,account.name)
                analytic_accout=self._create_analytic_accout(analytic_accout_name,department.id)
                #***********预算状况******************#
                budget_post_objs=self.env['account.budget.post'].search([('name','=',account.name)])
                if len(budget_post_objs)>0:
                    _logger.info('准备处理预算明细数据...')
                    parameter_values={}
                    parameter_values['analytic_account_id']=analytic_accout.id
                    parameter_values['general_budget_id']=budget_post_objs[0].id
                    parameter_values['start_date']=vals['date_from']
                    parameter_values['end_date']=vals['date_to']
                    parameter_values['total_amount']=vals.get('total_amount',0.00)
                    budget_lines=self._create_budget_line(parameter_values)
                    vals['crossovered_budget_line']=budget_lines
                else:
                    _logger.info('没有对应科目"%s"的预算状况，不创建预算明细...' % account.name)
            else:
                #***********不做任何处理******************#
                _logger.info('部门及科目至少有一项为空，不处理分析账号及预算明细...')

            return super(crossovered_budget,self).create(vals)

        except Exception as e:
            err_msg='新增预算出现异常：%s' % e.message
            _logger.error(err_msg)

    def _create_analytic_accout(self,name,department_id):
        '''
        功能：不存在“名称+部门”的分析账号时创建分析账号
        :param name:
        :param department_id:部门ID
        :return:分析账号
        '''
        try:
            _logger.info('接收到的参数，name=%s,deptment_id=%s' % (name,department_id))
            analytic_accout_instance=self.env['account.analytic.account']
            analytic_accout=analytic_accout_instance.search([('name','=',name),('department_id','=',department_id)])
            if not analytic_accout:
                _logger.info('需要创建分析账号')
                analytic_accout_value={}
                analytic_accout_value['name']=name
                analytic_accout_value['department_id']=department_id
                analytic_accout=analytic_accout_instance.create(analytic_accout_value)
            else:
                _logger.info('分析账号已存在，无需创建')
            return analytic_accout

        except Exception as e:
            err_msg='创建分析账号出现异常：%s' % e.message
            _logger.error(err_msg)

    def _create_budget_line(self,parameter_values):
        '''
        功能：根据会计期间、预算金额、预算状况、分析账号创建预算明细数据
        :param parameter_values:
        :return List,格式：[[0,False,{...}][0,False,{...}]]:
        '''
        budget_line_list=[]
        try:
            str_start_date=parameter_values['start_date']
            str_end_date=parameter_values['end_date']
            month_count=self._get_month_number(str_start_date,str_end_date)
            strptime_start=time.strptime(str_start_date,"%Y-%m-%d")
            # strptime_end=time.strptime(str_end_date,"%Y-%m-%d")
            # start_date=datetime.date(strptime_start.tm_year,strptime_start.tm_mon,strptime_start.tm_mday)
            # end_date=datetime.date(strptime_end.tm_year,strptime_end.tm_mon,strptime_end.tm_mday)
            # month_count=rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date).count()

            _logger.info('会计期间间隔为%s个月' % month_count)

            total_amount=parameter_values['total_amount']
            planned_amount=math.floor(total_amount/month_count)
            last_planned_amount=total_amount-planned_amount*(month_count-1)

            for i in range(0,month_count):
                line_value={}
                line_value['general_budget_id']=parameter_values['general_budget_id']
                line_value['analytic_account_id']=parameter_values['analytic_account_id']
                if i==month_count-1:
                    #最后一个月，存在尾差
                    line_value['planned_amount']=last_planned_amount
                else:
                    line_value['planned_amount']=planned_amount
                return_values=self._get_start_end_date(strptime_start,i)
                line_value['date_from']=return_values['start_date']
                line_value['date_to']=return_values['end_date']
                budget_line_list.append([0,False,line_value])

            return budget_line_list

        except Exception as e:
            err_msg='计算预算明细出现异常：%s' % e.message
            _logger.error(err_msg)

    def _get_start_end_date(self,day,n=0):
        '''
        功能：给定一个日期，返回下n个月的第一天和最后一天
        :param self:
        :param day:
        :param n:
        :return:
        '''
        try:
            month=day.tm_mon+n
            day_begin = '%d-%02d-01' % (day.tm_year, month)
            monthRange = calendar.monthrange(day.tm_year, month)
            strptime_start=time.strptime(day_begin,"%Y-%m-%d")
            start_date=datetime.date(strptime_start.tm_year,strptime_start.tm_mon,strptime_start.tm_mday)
            end_date=start_date + datetime.timedelta(days=monthRange[1]-1)
            return_values={}
            return_values['start_date']=start_date
            return_values['end_date']=end_date
            return  return_values

        except Exception as e:
            err_msg='_get_start_end_date异常:%s' % e.message
            _logger.error(err_msg)

    @api.onchange('company_id')
    def change_company(self):
        '''
        功能：公司变化时，清空部门
        :return:
        '''
        self.department_id=False

class crossovered_budget_line(osv.osv):
    '''
    功能：预算明细，增加字段“报销金额”
    '''
    _inherit ='crossovered.budget.lines'
    _columns = {
        'reimbursement_amount':fields.float(digits=(12, 2),string='报销金额')
    }
    # reimbursement_amount=fields.Float(digits=(12, 2),string='报销金额')


