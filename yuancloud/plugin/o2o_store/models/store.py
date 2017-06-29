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

def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


def geo_find(addr):
    url = 'http://apis.map.qq.com/ws/geocoder/v1/?key=OB4BZ-D4W3U-B7VVO-4PJWW-6TKDJ-WPB77&'
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise osv.except_osv(_('Network error'),
                             _(
                                 'Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None

class store_geo(models.TransientModel):
    _inherit = 'web_extended.map'
    # _name= 'store.geo'
    # _columns = {
    #     'addr': fields.char('address'),
    #     'company_id': fields.many2one('res.company'),
    #     'geo_latitude': fields.float('Geo Latitude', digits=(16, 5),
    #                                  default=lambda self: self._get_location('geo_latitude')),
    #     'geo_longitude': fields.float('Geo Longitude', digits=(16, 5),
    #                                   default=lambda self: self._get_location('geo_longitude')),
    #     'date_localization': fields.date('Geo Localization Date', default=lambda self: datetime.datetime.now()),
    # }

    @api.model
    def _get_location(self, field):
        store_id = self._context.get('active_id')
        if store_id:
            store = self.env['o2o.store'].search([('id', '=', store_id)])
            if store:
                if field == 'geo_latitude':
                    return store['latitude']
                if field == 'geo_longitude':
                    return store['longitude']

    @api.model
    def create(self, vals):
        # vals['company_id'] = self._context['active_id']
        # return super(store_geo, self).create(vals)
        return super(models.TransientModel, self).create(vals)
    @api.one
    def apply(self):
        o2o_store = self.env['o2o.store'].search([('id', '=', self._context['active_id'])])
        o2o_store.write({"latitude": self.geo_latitude, "longitude": self.geo_longitude, 'address': self.addr})
        # self.write({"latitude": self.latitude, "longitude": self.longitude})


def _country_get(obj, cr, uid, context=None):
    if context is None:
        context = {}
    ids = obj.pool.get('res.country').search(cr, uid, [('code', '=', 'CN')], context=context)
    if ids:
        # return ids[0]
        return obj.pool.get('res.country').browse(cr, uid, ids[0], context=context)
    return False


class o2o_store(osv.osv):
    '''
    实体：门店
    '''
    _name = 'o2o.store'
    _order = "name"

    # @api.one
    # def batch_gen_barcode(self):
    #     print self
    #     self.env['ycloud.qr.management'].gen_store_barcode(self.id)
    #     pass


    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'code': fields.char(required=True,string="编码"),
        'name': fields.char(required=True, string="门店名称"),
        'category': fields.many2one('o2o.storecategory', required=True, string="门店类别"),
        'category_line': fields.many2one('o2o.storecategory.line', string="门店小类"),
        'image': fields.binary("Image",
                               help="This field holds the image used as image for the store, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'o2o.store': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'o2o.store': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'contact': fields.char(string="联系人"),
        'phone': fields.char(string="电话"),
        'mail': fields.char(string='邮箱'),
        'fax': fields.char(string="传真"),
        'mobile': fields.char(string="手机号"),
        'country': fields.many2one('res.country', required=True, string="国家",
                                   default=lambda self: _country_get(self, self.env.cr, self.env.user.id)),
        'province': fields.many2one('res.country.state', required=True, string="省份"),
        'city': fields.char(required=True, string="城市"),
        'address': fields.char(required=True, string="详细地址"),
        'longitude': fields.float(string="经度", readonly=True),
        'latitude': fields.float(string="纬度", readonly=True),
        'business_hours': fields.char(required=True, string='营业时间'),
        'simple_info': fields.text(required=True, string="简介"),
        'recommend': fields.text(string="推荐"),
        'special_service': fields.text(string="特色服务"),
        'pos_ids': fields.many2many('pos.config', 'store_pos_rel', 'store_id', 'pos_id', string="POS"),
        'company_id': fields.many2one('res.company', string='公司'),
        'virtual_location': fields.many2one('stock.location',required=True, string='库位'),
        'store_owner': fields.many2one('res.users', string='店长'),
        'sale_team': fields.many2one('crm.team', '销售团队'),
        'images': fields.one2many('o2o.storeimages', 'store_id', string='门店图片'),
        'picking_type': fields.many2one("stock.picking.type", "分拣类型"),
        'users': fields.one2many('o2o.storeusers', 'store_id', string='门店员工'),
        # 'payment_agreement': fields.many2one('ycloud.base.paymentagreement', string='供应商协议'),
    }
    _sql_constraints = [('code_uniq', 'unique(code)', '编码必须唯一!')]

    def onchange_category(self, cr, uid, ids, category):
        '''
        功能：门店类别联动，更换门店类别时清空小类
        :param cr:
        :param uid:
        :param ids:
        :param category:
        :return:
        '''
        val = {
            'category_line': ''
        }
        return {'value': val}

    def onchange_country(self,cr,uid,ids,country):
        '''
        功能：国家变化时，清空省份
        :param cr:
        :param uid:
        :param ids:
        :param country:
        :return:
        '''
        val = {
            'province': ''
        }
        return {'value': val}

    @api.model
    def _default_company(self):
        '''
        功能：默认公司
        :return:
        '''
        return self.env['res.company']._company_default_get('res.partner')
    _defaults={
            'company_id': _default_company,
    }

    @api.model
    def create(self,vals):
        '''
        功能：重写create
        :param vals:
        :return:
        '''
        try :
            #检查门店编码是否符合规定（四位且首字母大写）
            code=vals['code']
            re_str='[A-Z]{1}[A-Z0-9]{3}'
            if len(code)!=4 or not re.match(re_str,code):
                msg='门店编码:%s,不满足门店编码规范：必须为"大写字母与数字组合的四位字符串"且"首字母大写"！' % vals['code']
                raise  except_osv(_('错误'), _(msg))

            #检查是否创建销售团队
            if (vals['store_owner'] or len(vals['users'])>0) and not vals['sale_team']:
                #创建销售团队
                sale_team=self.env['crm.team']
                sale_team_values={}
                sale_team_values['name']=vals['name']+'-销售团队'
                sale_team_values['code']=vals['code']
                #团队成员
                user_ids=[]
                if vals['store_owner']:
                    sale_team_values['user_id']=vals['store_owner']
                for userinfo in vals['users']:
                    user_ids.append(userinfo[2]['user_id'])
                member_ids=[[6, False, user_ids]]
                sale_team_values['member_ids']=member_ids
                sale_team_id=sale_team.create(sale_team_values)
                vals['sale_team']=sale_team_id.id

            #检查是否创建POS
            virtual_location=vals.get('virtual_location',False)
            company_id=vals.get('company_id',False)
            if not virtual_location and not company_id:
                if len(vals['pos_ids'])==0:
                    #创建POS
                    pos_instance=self.env['pos.config']
                    pos_value={}
                    pos_value['name']=vals['code']+'-POS'
                    pos_value['stock_location_id']=vals['virtual_location']
                    pos_value['company_id']=vals['company_id']
                    if vals['company_id']:
                        journals=self.env['account.journal'].search([('company_id','=',vals['company_id']),('journal_user','=','1')])
                        journal_ids=[]
                        for journal in journals:
                            journal_ids.append(journal.id)
                        pos_value['journal_ids']=[[6, False, journal_ids]]
                    pos_id=pos_instance.create(pos_value)
                    pos_ids=[[6, False, [pos_id.id]]]
                    vals['pos_ids']=pos_ids

            return  super(o2o_store, self).create(vals)
        except Exception as e:
            _logger.error(e)
            raise e

    @api.multi
    def write(self, vals):
        '''
        功能：重写write,验证门店编码是否符合规定
        :param vals:
        :return:
        '''
        try:
            for store in self:
                code=self.code
                if 'code' in vals:
                    code=vals['code']
                re_str='[A-Z]{1}[A-Z0-9]{3}'
                if len(code)!=4 or not re.match(re_str,code):
                    msg='门店编码:%s,不满足门店编码规范：必须为"大写字母与数字组合的四位字符串"且"首字母大写"！' % code
                    raise  except_osv(_('错误'), _(msg))

                return super(o2o_store, store).write(vals)
        except Exception as e:
            _logger.error(e)
            raise e

class o2o_storeimages(osv.osv):
    '''
    实体：门店图片定义
    '''
    _name = 'o2o.storeimages'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'store_id': fields.many2one('o2o.store'),
        'description': fields.char('描述'),
        'image': fields.binary("门店图片",
                               help="This field holds the image used as image for the store, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="门店中图", type="binary", multi="_get_image",
                                        store={
                                            'o2o.storeimages': (
                                                lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="门店小图", type="binary", multi="_get_image",
                                       store={
                                           'o2o.storeimages': (
                                               lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
    }

class o2o_storecategory(osv.osv):
    '''
    实体：门店类别
    '''
    _name = 'o2o.storecategory'
    _rec_name = 'name'
    _columns = {
        'code': fields.char(string="编码"),
        'name': fields.char(string="名称"),
        'lines': fields.one2many('o2o.storecategory.line', 'category_id', string='细分类')
    }
    _sql_constraints = [('code_uniq', 'unique(code)', '编码必须唯一!')]

class o2o_storecategory_line(osv.osv):
    '''
    实体：门店小类
    '''
    _name = 'o2o.storecategory.line'
    _columns = {
        'code': fields.char(string="编码"),
        'name': fields.char(string="名称"),
        'category_id': fields.many2one('o2o.storecategory', '门店分类', required=True, ondelete='cascade',
                                       select=True,
                                       readonly=True)
    }
    _sql_constraints = [('code_uniq', 'unique(code,category_id)', '门店分类＋小类编码名称必须唯一!')]

class o2o_storeusers(osv.osv):
    '''
    实体：门店员工，门店子表
    '''
    _name = 'o2o.storeusers'
    _rec_name = 'user_id'
    _columns = {
        'store_id': fields.many2one('o2o.store'),
        'user_id': fields.many2one('res.users', string='名称'),
        'phone': fields.char(string='电话', readonly=True, related='user_id.phone'),
        'mobile': fields.char(string='手机', readonly=True, related='user_id.mobile'),
        'fax': fields.char(string='传真', readonly=True, related='user_id.fax')
    }
