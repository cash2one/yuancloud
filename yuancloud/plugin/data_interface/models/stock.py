# -*- coding: utf-8 -*-
import itertools
from lxml import etree
import urllib2
import base64
from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools import float_compare
import yuancloud.addons.decimal_precision as dp
import datetime
import logging

_logger = logging.getLogger(__name__)

class stock_location(models.Model):
    '''
     库位：
    '''
    _inherit = 'stock.location'
    code =fields.Char(string='库位编码')

    @api.model
    def _location(self,**kwargs):
        code=kwargs['code']
        name=kwargs['name']
        exist_locations=self.env['stock.location'].search([('code','=',code)])
        wh_stock=self.env['stock.location'].search([('name','=',u'库存')])
        if len(exist_locations)==0:
            vals={}
            vals['code']=code
            vals['name']=name
            vals['location_id']=wh_stock.id
            return self.env['stock.location'].create(vals).id
        else:
            exist_locations[0].write({'name':name})
            return exist_locations[0].id