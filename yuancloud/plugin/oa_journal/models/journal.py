# -*- coding: utf-8 -*-
from yuancloud import models, fields, api
import datetime

def _employee_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
    if ids:
        return obj.pool.get('hr.employee').browse(cr, uid, ids[0], context=context)
    return False

class oa_journal(models.Model):
    '''
    模型：日常流水
    '''
    _name = 'oa.journal'
    _description = 'OA Journal'
    name = fields.Char('单号', required=True, select=True, copy=False, default=lambda obj: '/')
    item = fields.Many2one('product.product', string='料品')
    spec = fields.Char(string='规格')
    description = fields.Text(string='描述')
    total_debit = fields.Float(digits=(12, 2), string='金额', required=True)
    invoice_type = fields.Many2one('oa_journal.invoice.type', string='发票类型')
    mode_of_payment = fields.Selection(
        [('Cash', '现金'), ('Tenpay', '财付通支付'), ('Alipay', '支付宝支付'), ('Transfer', '网银转账'),
         ('Credit', '信用卡支付'), ('Wechat', '微信支付')], string='支付方式', required=True)
    payer_employee = fields.Many2one('hr.employee', string="付款人", required=True,
                                     default=lambda self: _employee_get(self, self.env.cr, self.env.user.id))
    paidon = fields.Datetime(string='付款时间', required=True, default=lambda self: datetime.datetime.now())
    supplier = fields.Many2one('res.partner', string='供应商')
    supplier_order = fields.Char(string='供应商单号')
    receivedon = fields.Datetime(string='收货时间')
    storage_location = fields.Char(string='存储地点')
    collar_employee = fields.Many2one("hr.employee", string='领用人')
    address = fields.Char(string='地址')
    expense_claim = fields.Many2one('hr.expense.expense', string='报销单')
    claim_amount = fields.Float(digits=(12, 2),string='销抵金额')
    state = fields.Selection([('draft', '草稿'), ('paid', '已付款'), ('received', '已收货'), ('expensed', '已报销'),
                              ('closed', '已关闭')], string='状态', readonly=True, default='draft')
    ec_platform = fields.Many2one("oa_journal.ecplatform", string='电商平台')
    extend_col1 = fields.Char(string='扩展字段1')
    company_id = fields.Many2one("res.company", string='公司')

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', '单号必须唯一!')
    ]
    _order = "name desc"

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('oa.journal') or '/'

        _defaults = {
            'name': '/',
        }
        return super(oa_journal, self).create(vals)
