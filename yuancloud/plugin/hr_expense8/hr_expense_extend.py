# -*- coding: utf-8 -*-

# from openerp import models, fields, api

import itertools
from lxml import etree

from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
import datetime

# inherite from hr.expense
class Expense(models.Model):
    _inherit = 'hr.expense8.expense'

    name = fields.Char('Name', required=True, select=True, copy=False, default=lambda obj: '/')
    description = fields.Char('Description', readonly=True,
                              states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Order Reference must be unique per Company!')
    ]

    _order = "name desc"

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.expense8.expense') or '/'

        _defaults = {
            'name': '/',
        }
        return super(Expense, self).create(vals)


# inherite from hr.expense.line
class expense_line(models.Model):
    _inherit = 'hr.expense8.line'
    product_id = fields.Many2one('product.product', '费用类型', domain=[('hr_expense_ok', '=', True)], required=True)
