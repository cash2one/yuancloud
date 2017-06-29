# -*- coding: utf-8 -*-
from yuancloud import models, tools, fields, api, _
from yuancloud.osv.osv import except_osv

class stock_move(models.Model):
    '''
    库存移动实体扩展，增加批次
    '''
    _inherit = "stock.move"
    lot_id=fields.Many2one('stock.production.lot',string='批次')