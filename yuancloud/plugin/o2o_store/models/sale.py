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

class sale_order(models.Model):
    '''
    实体扩展：销售订单扩展字段：门店，门店编码
    '''
    _inherit = 'sale.order'
    store_id=fields.Many2one('o2o.store','门店')
    store_code=fields.Char(string='门店编码')

    @api.onchange('store_id')
    def store_change(self):
        '''
        功能：门店
        :return: 变更时，填充门店编码
        '''
        try:
            if self.store_id:
                self.store_code=self.store_id.code
        except Exception as e:
            _logger.error(e)