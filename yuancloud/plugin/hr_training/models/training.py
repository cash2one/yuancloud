# -*- coding: utf-8 -*-
from yuancloud import models, tools, fields, api, _
from yuancloud.osv.osv import except_osv
import logging

_logger = logging.getLogger(__name__)

class training_lession(models.Model):
    '''
    实体：培训课程
    '''
    _name = 'hr.training.lession'

    type=fields.Selection([('Internal','内部培训'),('External','外部培训')],default='Internal',required=True,string='课程类型')
    code=fields.Char(required=True,string='课程编号')
    name=fields.Char(required=True,string='课程名称')
    teacher=fields.Many2many('hr.employee', 'lession_teacher_rel', 'lession_id', 'teacher_id',string='内聘讲师')
    external_teacher=fields.Char(string='外聘讲师')
    price=fields.Float(digits=(16,2),string='培训费用',default=0.0)
    description = fields.Text(string='课程描述')

    _sql_constraints = [('code_uniq', 'unique(code)', '课程编号必须唯一!')]

class training(models.Model):
    '''
    实体：培训记录
    '''
    _name = 'hr.training.record'

    lession_id=fields.Many2one('hr.training.lession',string='培训课程',required=True,)
    date=fields.Date(required=True,string='培训日期')
    time=fields.Char(required=True,string='培训时间')
    address=fields.Char(required=True,string='培训地点')
    teacher=fields.Char(required=True,string='培训讲师')
    student=fields.Many2many('hr.employee', 'training_employee_rel', 'training_id', 'employee_id',required=True,string='培训学员')
    price=fields.Float(digits=(16,2),string='培训费用',default=0.0)
    description = fields.Text(string='培训描述')

    @api.onchange('lession_id')
    def change_lession(self):
        '''
        功能：默认根据课程获取培训费用、培训讲师
        :return:
        '''
        if self.lession_id:
            self.price=self.lession_id.price
            teachers=''
            if self.lession_id.external_teacher:
                teachers=self.lession_id.external_teacher+','

            #取内聘讲师
            sql_str = '''select emp.name_related from lession_teacher_rel as r join hr_employee as emp on r.teacher_id=emp.id
                              where r.lession_id=%s
                              ''' % (self.lession_id.id)

            _logger.info('根据培训课程ID，查找讲师=%s' % sql_str)
            self._cr.execute(sql_str)
            res = self._cr.fetchall()
            for r in res:
                teachers+=r[0]+','
            if len(teachers)>0:
                teachers=teachers[0:-1]

            self.teacher=teachers
            self.description=self.lession_id.description