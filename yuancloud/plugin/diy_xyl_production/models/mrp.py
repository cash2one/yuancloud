# -*- coding: utf-8 -*-
from yuancloud import models, tools, fields, api, _
from yuancloud.osv.osv import except_osv

class mrp_production_workcenter_line_extend(models.Model):
    '''
    派工单（工票）实体扩展
    '''
    _inherit = 'mrp.production.workcenter.line'
    _description = 'Work Order'
    _order = 'sequence'
    plan_qty=fields.Float(digits=(16,2),string='计划数量')
    actual_qty=fields.Float(digits=(16,2),string='实际数量')
    qualified_qty=fields.Float(digits=(16,2),string='实际合格量')
    finish_user=fields.Many2many('res.users','finish_plan_user_rel','finish_plan_id','user_id',string='操作人员')
    is_comp_point=fields.Boolean(string='完工报告点')
    is_finish_plan=fields.Boolean(string='捕捞计划')
    lot_id=fields.Many2one('stock.production.lot',string='批次')

class mrp_routing_workcenter_extend(models.Model):
    """
    工序实体扩展：是否完工报告点
    """
    _inherit = 'mrp.routing.workcenter'
    is_comp_point=fields.Boolean(string='完工报告点')

