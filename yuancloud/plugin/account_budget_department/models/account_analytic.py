# -*- coding: utf-8 -*-
from yuancloud import models, fields, api
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
_logger = logging.getLogger(__name__)

class account_analytic_account(models.Model):
    '''
    功能：“分析账户”增加“部门”
    '''
    _inherit = "account.analytic.account"

    department_id=fields.Many2one('hr.department',string='部门')