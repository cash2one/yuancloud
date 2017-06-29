# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from yuancloud import tools
from yuancloud.osv import fields, osv
from yuancloud.addons.decimal_precision import decimal_precision as dp


class oa_journal_report(osv.osv):
    _name = "oa.journal.report"
    _description = "OA Journal Statistics"
    _auto = False
    _rec_name = 'paidon'
    _columns = {
        'create_date': fields.datetime('创建时间', readonly=True),
        'invoice_type': fields.many2one('oa_journal.invoice.type', string="发票类型", readonly=True),
        'total_debit': fields.float(digits=(12, 2), string="金额", readonly=True),
        'mode_of_payment': fields.selection(
            [('Cash', '现金'), ('Tenpay', '财付通支付'), ('Alipay', '支付宝支付'), ('Transfer', '网银转账'),
             ('Credit', '信用卡支付'), ('Wechat', '微信支付')], string="付款方式", readonly=True),
        'payer_employee': fields.many2one("hr.employee", string="付款人", readonly=True),
        'paidon': fields.datetime(string="付款时间", readonly=True),
        'collar_employee': fields.many2one("hr.employee", "领用人", readonly=True),
        'state': fields.selection(
            [('draft', '草稿'), ('paid', '已付款'), ('received', '已收获'), ('expensed', '已报销'),
             ('closed', '关闭')], string="状态", readonly=True),
        'ec_platform': fields.many2one("oa_journal.ecplatform", '电商平台', readonly=True)
    }
    _order = 'paidon desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'oa_journal_report')
        cr.execute("""
            create or replace view oa_journal_report as (
                 select * from oa_journal
            )
        """)
