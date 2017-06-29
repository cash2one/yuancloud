# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

from yuancloud.osv import fields, osv

class hr_payroll_configuration(osv.osv_memory):
    _name = 'hr.payroll.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'module_hr_payroll_account': fields.boolean('Link your payroll to accounting system',
            help ="""Create journal entries from payslips"""),
    }
