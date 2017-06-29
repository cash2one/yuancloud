# -*- coding: utf-8 -*-
from yuancloud import models, tools, fields, api, _
import time,datetime
from yuancloud.osv.osv import except_osv
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

class hr_employee(models.Model):
    '''
    实体：员工档案，字段扩展
    '''
    _inherit = 'hr.employee'
    educatio_type = [
        ('middle_school', '初中'),
        ('high_school', '高中'),
        ('diploma', '大专'),
        ('benco', '本科'),
        ('master', '硕士研究生'),
        ('doctor', '博士研究生'),
    ]
    degrees_type = [
        ('middle_school', '学士'),
        ('high_school', '硕士'),
        ('diploma', '博士'),
    ]
    training_methods_type = [
        ('series_incur', '统招'),
        ('self-taught', '自考'),
        ('adult_education', '成教'),
        ('tv_university', '电大&夜大'),
    ]
    category_type = [
        ('OM', '管理'),
        ('A', '职能'),
        ('S', '销售'),
        ('CRTE', '技术'),
    ]
    job_titile_type = [
        ('O', '经营管理'),
        ('M', '一般管理'),
        ('A', '行政职能'),
        ('S', '业务营销'),
    ]
    marriage_type = [
        ('unmarried', '未婚未育'),
        ('unmarried_pregnant', '未婚已育'),
        ('married', '已婚未育'),
        ('married_pregnant', '已婚已育'),
    ]
    household_type = [
        ('city_town', '本市城镇'),
        ('city_village', '本市农业'),
        ('other_town', '外埠城镇'),
        ('other_village', '外埠农业'),
    ]
    learning_style = [
        ('full_time', '脱产'),
        ('part_time', '半脱产'),
        ('job', '在职'),
    ]
    employment_type = [
        ('internship', '实习'),
        ('trial', '试用'),
        ('formally', '正式'),
        ('employ', '聘用（含劳务）'),
    ]

    service_state_type = [
        ('entry_employee', '入职员工'),
        ('regular_employee', '转正员工'),
        ('mobilize_employee', '调动员工'),
        ('leave_employee', '离职员工'),
    ]

    code=fields.Char(string='员工代号')
    country_id=fields.Many2one('res.country', string="国家",default=lambda self: _country_get(self, self.env.cr, self.env.user.id))
    province_id=fields.Many2one('res.country.state',string="省份")
    university=fields.Char(string='毕业院校')
    educatio=fields.Selection(educatio_type,string='学历')
    degrees=fields.Selection(degrees_type,string='学位')
    profession=fields.Char(string='专业')
    training_methods=fields.Selection(training_methods_type,string='培养方式')
    admission_date=fields.Date(string='入学日期')
    graduation_date=fields.Date(string='毕业日期')
    ext=fields.Char(string='分机号')

    category=fields.Selection(category_type,string='职类')
    job_titile=fields.Selection(job_titile_type,string='职别')
    grade=fields.Char(string='职等')
    marriage=fields.Selection(marriage_type,string='婚育')
    household=fields.Selection(household_type,string='户口性质')
    learning=fields.Selection(learning_style,string='学习方式')
    #其他页签
    urgent_contacts=fields.Char(string='紧急联系人')
    urgent_contacts_mobile=fields.Char(string='紧急联系人手机')
    urgent_contacts_phone=fields.Char(string='紧急联系人座机')
    urgent_contacts_relation=fields.Char(string='紧急联系人关系')

    #用工类型
    employment= fields.Selection(employment_type,string='用工类型',default='formally')
    induction_date=fields.Date(string='入职日期')
    formally_date=fields.Date(string='转正日期')
    exit_date=fields.Date(string='离职日期')

    #社保信息
    social_insurance_years=fields.Integer(string='社保缴费年',help='填写社保机构出具或查询到的社保缴费年数')
    social_insurance_months=fields.Integer(string='社保缴费月',help='填写社保机构出具或查询到的社保缴费月数')

    #工龄
    working_years_prove=fields.Binary(string='工龄证明')
    pre_job_seniority=fields.Float(digits=(16,2),string='入职前工龄',help='根据入职前提供的“社保缴费年限”证明或者存档机构出具的“工龄证明”核定入职前工龄，一经核定不允许修改')
    company_years=fields.Float(compute='_compute_company_years',string='司龄')
    now_working_years=fields.Float(compute='_methods_now_working_years',string='现工龄')

    nation=fields.Char(string='民族')
    birthday=fields.Date(compute="_compute_birthday",string='出生日期',store=True)
    age=fields.Integer(compute="_compute_ages",string='年龄',store=True)
    service_state=fields.Selection(service_state_type,string='在职状态',default='entry_employee')

    # contract_id=fields.Many2one('hr.contract',string='现合同')

    def _caltime(self,date1,date2):
        date1=time.strptime(date1,"%Y-%m-%d")
        date2=time.strptime(date2,"%Y-%m-%d")
        date1=datetime.datetime(date1[0],date1[1],date1[2])
        date2=datetime.datetime(date2[0],date2[1],date2[2])
        return date2-date1

    @api.one
    @api.depends('induction_date','service_state','exit_date')
    def _compute_company_years(self):
        '''
        根据入职日期计算司
        :return:
        '''
        current_date=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        end_date=current_date
        if self.service_state=='leave_employee' and self.exit_date:
            end_date=self.exit_date
        if self.induction_date:
            self.company_years = self._caltime(self.induction_date,end_date).days/365.00
        else:
            self.company_years=0.00

    @api.one
    @api.depends('pre_job_seniority','company_years')
    def _methods_now_working_years(self):
        '''
        根据入职前工龄与司龄计算现工龄
        :return:
        '''
        self.now_working_years = self.pre_job_seniority + self.company_years

    @api.one
    @api.depends('identification_id')
    def _compute_birthday(self):
        '''
        根据身份证号计算出生日期
        :return:
        '''
        year=''
        month=''
        day=''
        if self.identification_id:
            if len(self.identification_id)==18:
                year=self.identification_id[6:10]
                month=self.identification_id[10:12]
                day=self.identification_id[12:14]

            if len(self.identification_id)==16:
                year='19'+self.identification_id[6:8]
                month=self.identification_id[8:10]
                day=self.identification_id[10:12]
            str_birthday="%s-%s-%s" % (year,month,day)
            self.birthday=datetime.datetime(int(year),int(month),int(day))
            # self._compute_ages()

    @api.one
    @api.depends('birthday')
    def _compute_ages(self):
        '''
        根据出生日期计算年龄
        :return:
        '''
        current_date=time.strftime('%Y-%m-%d',time.localtime(time.time()))
        if self.birthday:
            self.age = self._caltime(self.birthday,current_date).days / 365
        else:
            self.age=0

    @api.model
    def create(self, vals):
        '''
        功能：员工代号未维护，找编码规则；维护了则验证是否重复
        :param vals:
        :return:
        '''
        code=vals.get('code',False)
        if not code:
            vals['code'] = self.env['ir.sequence'].get('hr.employee')
        else:
            exis_emps=self.env['hr.employee'].search([('code','=',code),('id','!=',self.id)])
            if len(exis_emps)>0:
                exis_emp_names=''
                for exis_emp in exis_emps:
                    exis_emp_names=exis_emp_names+exis_emp.name+','
                msg='员工代号%s重复（具有该员工代号的员工有%s）！' % (code,exis_emp_names[0:-1])
                raise  except_osv(_('错误'), _(msg))

        return super(hr_employee, self).create(vals)

    @api.multi
    def write(self, vals):
        '''
        功能：员工代号不能重复
        :param vals:
        :return:
        '''
        try:
            for employee in self:
                code=vals.get('code',False)
                if code:
                    exis_emps=self.env['hr.employee'].search([('code','=',code),('id','!=',employee.id)])
                    if len(exis_emps)>0:
                        exis_emp_names=''
                        for exis_emp in exis_emps:
                            exis_emp_names=exis_emp_names+exis_emp.name+','
                        msg='员工代号%s重复（具有该员工代号的员工有%s）！' % (code,exis_emp_names[0:-1])
                        raise  except_osv(_('错误'), _(msg))
                return super(hr_employee, employee).write(vals)

        except Exception as e:
            _logger.error(e)
            raise e


class hr_department(models.Model):
    '''
    实体：部门档案，字段扩展
    '''
    _inherit = 'hr.department'
    code=fields.Char(string='部门编码')





