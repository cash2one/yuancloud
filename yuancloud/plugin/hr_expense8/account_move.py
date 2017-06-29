# -*- coding: utf-8 -*-
import itertools
from lxml import etree

from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
import datetime
import logging

_logger = logging.getLogger(__name__)

class account_move(models.Model):
    '''
    '''
    _inherit = 'account.move'

    def account_move_prepare(self, cr, uid, journal_id, date=False, ref='', company_id=False, context=None):
        '''
        Prepares and returns a dictionary of values, ready to be passed to create() based on the parameters received.
        '''
        if not date:
            date = fields.date.today()
        period_obj = self.pool.get('account.period')
        if not company_id:
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            company_id = user.company_id.id
        if context is None:
            context = {}
        #put the company in context to find the good period
        ctx = context.copy()
        ctx.update({'company_id': company_id})
        return {
            'journal_id': journal_id,
            'date': date,
            'period_id': period_obj.find(cr, uid, date, context=ctx)[0],
            'ref': ref,
            'company_id': company_id,
        }

# class account_perid(models.Model) :
#     _inherit = 'account.period'
#     @api.returns('self')
#     def find(self, cr, uid, dt=None, context=None):
#         if context is None: context = {}
#         if not dt:
#             dt = fields.date.context_today(self, cr, uid, context=context)
#         args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
#         if context.get('company_id', False):
#             args.append(('company_id', '=', context['company_id']))
#         else:
#             company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
#             args.append(('company_id', '=', company_id))
#         result = []
#         if context.get('account_period_prefer_normal', True):
#             # look for non-special periods first, and fallback to all if no result is found
#             result = self.search(cr, uid, args + [('special', '=', False)], context=context)
#         if not result:
#             result = self.search(cr, uid, args, context=context)
#         if not result:
#             model, action_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account', 'action_account_period')
#             msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.') % dt
#             # raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
#         return result