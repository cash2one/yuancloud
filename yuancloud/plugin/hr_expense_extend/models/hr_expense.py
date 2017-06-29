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


class hr_expense(models.Model):
    '''
    功能：扩展费用字段：审批历史，当前审批角色
    '''
    _inherit ='hr.expense'
    #分析会计字段，设置为必输项
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', states={'post': [('readonly', True)], 'done': [('readonly', True)]}, oldname='analytic_account',required=True)
    #新增以下字段
    max_approval_level=fields.Integer(string='最高审批等级')
    current_approval_level=fields.Integer(string='当前审批等级',default=0)
    approval_history=fields.Char(string='审批历史')

    _order = 'date'

    @api.model
    def _employee_get(self):
        '''
        功能：取当前用户关联的员工名称
        :return:
        '''
        employee=self.env['hr.employee'].search([('user_id','=',self._uid)])
        if employee:
            return employee[0].name
        return '未能取到id=%s的用户对应的员工' % self._uid

    def _get_max_approval_level(self,unit_amount):
        '''
        功能：最大审批等级
        :param unit_amount:
        :return:
        '''
        try:
            max_approval_level=1
            #注意：按审批等级排序
            expense_approval_objs=self.env['hr.expense.approval'].search([],order='level')
            for expense_approval_obj in expense_approval_objs:
                if unit_amount<=expense_approval_obj.max_amount:
                    max_approval_level=expense_approval_obj.level
                    break
            return max_approval_level
        except Exception as e:
            err_msg='获取最大审批等级异常:%s' % e.message
            _logger.error(err_msg)

    @api.model
    def create(self, vals):
        '''
        功能：重写create,主要目的：确认最大审批等级
        :param vals:
        :return:
        '''
        # unit_amount=vals['unit_amount']
        # max_approval_level=self._get_max_approval_level(unit_amount)
        # vals['max_approval_level']=max_approval_level
        # hr_expense_obj=super(hr_expense,self).create(vals)
        # return hr_expense_obj
        try:
            #计算最高审批等级
            unit_amount=vals['unit_amount']
            max_approval_level=self._get_max_approval_level(unit_amount)
            vals['max_approval_level']=max_approval_level
            hr_expense_obj=super(hr_expense,self).create(vals)
            return hr_expense_obj
        except Exception as e:
            err_msg='新增费用异常，%s' % e.message
            _logger.error(err_msg)
            raise e

    @api.multi
    def write(self, vals):
        '''
        功能：重写write,目的：可能调整最大审批等级
        '''
        try:
            #计算最高审批等级
            unit_amount=vals.get('unit_amount',False)
            if unit_amount:
                max_approval_level=self._get_max_approval_level(unit_amount)
                vals['max_approval_level']=max_approval_level
            return super(hr_expense,self).write(vals)

        except Exception as e:
            err_msg='更新费用异常，%s' % e.message
            _logger.error(err_msg)
            raise e

    @api.multi
    def submit_expenses(self):
        '''
        功能：
        :return:
        '''
        try:
            for expense in self:
                result=self._validate_expense(expense)
                success= result.get('success',True)
                if not success:
                    raise except_osv(_('错误'), _(result.get('error_msg',True)))

            super(hr_expense,self).submit_expenses()
        except Exception as e:
            err_msg='"提交给经理"操作出现异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise except_osv(('错误'), (err_msg))

    @api.model
    def _validate_expense(self,expense):
        '''
        功能：验证预算是否超支等,是否存在预算科目，本期是否有预算
             校验没问题，回写预算明细报销金额
        :param expense:
        :return:
        '''
        result={}
        success=True
        error_msg=False
        try:
            _logger.info('"提交给经理"操作开始进行校验...')
            expense_admin=self.env['hr.expense'].sudo().search([('id','=',expense.id)])
            if expense_admin.analytic_account_id:
                account_id=expense_admin.product_id.property_account_expense_id
                total_account=expense_admin.total_amount
                date_value=expense_admin.date
                for budget_line in expense_admin.analytic_account_id.crossovered_budget_line:
                    if account_id not in budget_line.general_budget_id.account_ids:
                        success=False
                        error_msg='没有"%s"的预算费用!' % account_id.name
                        _logger.info(error_msg)
                    else:
                        date_from=int(budget_line.date_from.replace('-',''))
                        date_to=int(budget_line.date_to.replace('-',''))
                        if int(date_value.replace('-','')) in range(date_from,date_to):
                            planned_amount=budget_line.planned_amount #计划金额
                            reimbursement_amount=budget_line.reimbursement_amount#报销金额
                            r_amount=abs(planned_amount-reimbursement_amount) #可报销金额
                            info_msg='%s至%s期间预算金额=%s;已报销金额=%s;可报销金额=%s' % (budget_line.date_from,budget_line.date_to,planned_amount,reimbursement_amount,r_amount)
                            _logger.info(info_msg)
                            if total_account>r_amount:
                                success=False
                                error_msg=info_msg+',已超出预算！'
                                _logger.info(error_msg)
                            else:
                                _logger.info('可以报销，准备回写预算明细的报销金额...')
                                success=True
                                budget_line.reimbursement_amount+=total_account
                            break #退出循环
                        else:
                            success=False
                            error_msg='%s未在预算时间范围内!' % date_value
                            _logger.info(error_msg)
        except Exception as  e:
            success=False
            err_msg='校验异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(error_msg)
        finally:
            result['success']=success
            result['error_msg']=error_msg
            return result

    @api.multi
    def approve_expenses(self):
        '''
        功能：“同意”审批逻辑重写
        :return:
        '''
        try:
            user_approval_level=self._validate_approval() #校验,无异常时返回当前用户可审批等级的集合
            levels=[] #当前用户可连续审批的集合
            for i in range(0,len(user_approval_level)):
                if i==0:
                    levels.append(user_approval_level[i])
                elif user_approval_level[i]<>user_approval_level[i-1]+1:
                    break
                else:
                    levels.append(user_approval_level[i])
            if levels:
                #当前用户可连续审批的等级，一次性执行完成
                for level in levels:
                    if level>=self.current_approval_level:
                        approval_history=self.approval_history
                        if approval_history:
                            approval_history+='-->%s[%s级]' % (self._employee_get(),level+1)
                        else:
                            approval_history='%s[%s级]' % (self._employee_get(),level+1)
                        current_approval_level=level+1 #当前应几级审批
                        update_values={}
                        update_values['approval_history']=approval_history
                        update_values['current_approval_level']=current_approval_level
                        self.write(update_values)
                        if current_approval_level==self.max_approval_level:
                            self.write({'state': 'approve'})
                            break

        except Exception as e:
            err_msg='批准异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise except_osv(('错误'), (err_msg))

    @api.multi
    def refuse_expenses(self, reason):
        '''
        功能：“拒绝”操作重写
        :param reason:
        :return:
        '''
        try:
            self._validate_approval() #校验
            self.write({'state': 'cancel'})
            if self.employee_id.user_id:
                body = (_("Your Expense %s has been refused.<br/><ul class=o_timeline_tracking_value_list><li>Reason<span> : </span><span class=o_timeline_tracking_value>%s</span></li></ul>") % (self.name, reason))
                self.message_post(body=body, partner_ids=[self.employee_id.user_id.partner_id.id])

            # 扣减报销金额
            _logger.info('准备扣减预算明细的报销金额...')
            success=False
            expense_admin=self.env['hr.expense'].sudo().search([('id','=',self.id)])
            if expense_admin.analytic_account_id:
                account_id=expense_admin.product_id.property_account_expense_id
                total_account=expense_admin.total_amount
                date_value=expense_admin.date
                for budget_line in expense_admin.analytic_account_id.crossovered_budget_line:
                    if account_id not in budget_line.general_budget_id.account_ids:
                        pass
                    else:
                        date_from=int(budget_line.date_from.replace('-',''))
                        date_to=int(budget_line.date_to.replace('-',''))
                        if int(date_value.replace('-','')) in range(date_from,date_to):
                            success=True
                            _logger.info('找到可扣减项：科目=%s中的预算区间为%s至%s的明细中的报销金额...' % (account_id.name,budget_line.date_from,budget_line.date_to))
                            budget_line.reimbursement_amount-=total_account
                            _logger.info('扣减成功')
                            break #退出循环
            if not success:
                _logger.info('未能找到可扣减的预算明细！')

        except Exception as e:
            err_msg='拒绝异常，%s' % e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise except_osv(('错误'), (err_msg))

    def _validate_approval(self):
        '''
        功能：校验是否可以进行批准与拒绝
        :return:
        '''
        try:
            user_approval_level=self._get_current_approval_level()['approval_levels_int']
            str_user_approval_level=''
            for level in user_approval_level:
                str_user_approval_level+=str(level+1)+','
            if len(str_user_approval_level)>0:
                str_user_approval_level=str_user_approval_level[:-1]
            _logger.info('当前用户可审批%s等级的费用')
            current_approval_level=self.current_approval_level
            if current_approval_level not in user_approval_level:
                msg='目前应由%s级审批人处理，您是%s级审批人，不允许进行“批准”或“拒绝”操作！' % (current_approval_level+1,str_user_approval_level)
                raise except_osv(('错误'), (msg))
            else:
                return user_approval_level

        except Exception as e:
            err_msg=e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            raise except_osv(('错误'), (err_msg))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        功能：动态修改"待审批"的过滤条件
        :param view_id:
        :param view_type:
        :param toolbar:
        :param submenu:
        :return:
        '''
        res = super(hr_expense, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//filter[@name='submitted']"):
            current_approval_level=self._get_current_approval_level()['approval_levels_str']
            str_domain="[('state', '=', 'submit'),('current_approval_level','in',%s)]" % current_approval_level
            node.set('domain', str_domain)
        res['arch'] = etree.tostring(doc)
        return res

    def _get_current_approval_level(self):
        '''
        功能：通过用户ID，获取该用户属于几级审批人
        :return:
        '''
        approval_levels_str=[]
        approval_levels_int=[]
        sql_str = '''select distinct level from res_groups_users_rel as rel
                      join hr_expense_approval as approval on rel.gid=approval.group_id where rel.uid=%s
                      ''' % self._uid
        _logger.info('根据用户ID获取审批等级的SQL=%s' % sql_str)
        self._cr.execute(sql_str)
        res = self._cr.fetchall()
        for r in res:
            approval_levels_str.append(str(r[0]-1))
            approval_levels_int.append(r[0]-1)
        if not approval_levels_str:
            approval_levels_str=['-1']
        if not approval_levels_int:
            approval_levels_int=[-1]
        result={}
        result['approval_levels_str']=approval_levels_str
        result['approval_levels_int']=approval_levels_int
        return result


class hr_expense_approval(models.Model):
    '''
    功能：配置费用报销的审批流程
    '''
    _name = 'hr.expense.approval'
    level=fields.Integer(string='审批等级')
    group_id=fields.Many2one('res.groups',string='审批组')
    max_amount=fields.Integer(string='最大审批额度')

