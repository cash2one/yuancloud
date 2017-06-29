# -*- coding: utf-8 -*-
# from openerp import models, fields, api
import itertools
import json
from lxml import etree
import urllib
from yuancloud import models, tools, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare, werkzeug
from yuancloud.tools.translate import _
from yuancloud.tools import DEFAULT_SERVER_DATETIME_FORMAT

import yuancloud.addons.decimal_precision as dp
from yuancloud.tools.translate import _
from yuancloud.osv import osv, fields, expression
from yuancloud.osv.osv import except_osv
import logging
_logger = logging.getLogger(__name__)
import re
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class hr_payroll_run_extend(models.Model):
    _inherit = 'hr.payslip.run'

    @api.multi
    def print_payroll(self):
        return self.env['report'].get_action(self, 'hr_payroll_extend.report_payroll')