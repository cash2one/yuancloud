# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

import time

from yuancloud import SUPERUSER_ID
from yuancloud.osv import fields, osv

class hr_employee(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    def _trainings_count(self, cr, uid, ids, field_name, arg, context=None):
        Training = self.pool['hr.training.record']
        sql_str = '''select rel.*,emp.* from training_employee_rel as rel join hr_employee as emp on rel.employee_id = emp.id
                              where emp.id=%s
                              ''' % (ids[0])
        # _logger.info('根据培训课程ID，查找讲师=%s' % sql_str)
        self._cr.execute(sql_str)
        res = self._cr.fetchall()
        return {ids[0]:len(res)}

    _columns = {
        'trainings_count': fields.function(_trainings_count, type='integer', string='Trainings'),
    }