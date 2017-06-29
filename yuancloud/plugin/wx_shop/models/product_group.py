# -*- coding: utf-8 -*-

# from openerp import models, fields, api
try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields, api
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv

from yuancloud.addons.wx_base.sdks.officalaccount_sdk import group_manager

import time

#解码错误
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#日志
import logging
_logger = logging.getLogger(__name__)

class wx_product_group(models.Model):
    '''
    实体：微信商品分组
    '''
    _name = 'wx.productgroup'
    _rec_name = "wx_group_name"
    wx_officialaccount = fields.Many2one('wx.officialaccount', string='服务号', required=True)
    wx_group_id = fields.Char("分组ID")
    wx_group_name = fields.Char("分组名称", required=True)
    _sql_constraints = [
        ('group_uniq', 'unique(wx_officialaccount, wx_group_name)', '同一服务号下分组名称不能重复!')
    ]

    @api.model
    def create(self, vals):
        '''
        功能：创建小店分组
        :param vals:
        :return:
        '''
        try:
            if 'wx_group_id' not in vals:
                wx_officialaccount_id = vals['wx_officialaccount']
                wx_officialaccount = self.env['wx.officialaccount'].search([('id', '=', wx_officialaccount_id)])
                appid = wx_officialaccount.wx_appid
                appsecret = wx_officialaccount.wx_appsecret
                group_help = group_manager.group_manager(appid, appsecret)
                result = group_help.add_group(vals['wx_group_name'])
                if result['errcode'] == 0:
                    vals['wx_group_id'] = result['group_id']
                else:
                    _logger.info("创建微信小店分组错误：%s" % result['errmsg'])
            #add self
            return super(wx_product_group, self).create(vals)

        except Exception as e:
            _logger.error(e)

    @api.multi
    def write(self, vals):
        '''
        功能：更新小店分组
        :param vals:
        :return:
        '''
        try:
            for product_group in self:
                appid = product_group.wx_officialaccount.wx_appid
                appsecret = product_group.wx_officialaccount.wx_appsecret
                group_help = group_manager.group_manager(appid, appsecret)
                result = group_help.modify_group(int(product_group.wx_group_id), vals['wx_group_name'])
                if result['errcode'] == 0:
                    return super(wx_product_group, product_group).write(vals)
                    _logger.info("更新微信小店分组成功：%s" % result['errmsg'])
                else:
                    _logger.info("更新微信小店分组错误：%s" % result['errmsg'])
        except Exception as e:
            _logger.error(e)

    @api.multi
    def unlink(self):
        '''
        功能：删除小店分组
        :return:
        '''
        try:
            for product_group in self:
                appid = product_group.wx_officialaccount.wx_appid
                appsecret = product_group.wx_officialaccount.wx_appsecret
                group_help = group_manager.group_manager(appid, appsecret)
                # result = group_help.getbyid_group(int(product_group.wx_group_id))
                # if result['errcode'] == 0:
                del_result = group_help.del_group(int(product_group.wx_group_id))
                if del_result['errcode'] == 0:
                    return super(wx_product_group, product_group).unlink()
                    _logger.info("删除微信小店分组成功：%s" % del_result['errmsg'])
                else:
                    _logger.info("删除微信小店分组错误：%s" % del_result['errmsg'])
        except Exception as e:
            _logger.error(e)
            raise e

class wx_sync_group(models.Model):
    '''
    功能：微信商品分组，通过服务号获取该服务号查找对应小店的，以便抓取小店的商品分组
    '''
    _name = 'wx.syncgroup'
    wx_officialaccount = fields.Many2one('wx.officialaccount', required=True,string='服务号')

    @api.one
    def sync_group(self):
        try:
            appid = self.wx_officialaccount.wx_appid
            appsecret = self.wx_officialaccount.wx_appsecret
            group_help = group_manager.group_manager(appid, appsecret)
            result = group_help.getall_group()
            wx_productgroup_obj = self.env['wx.productgroup']
            if result['errcode'] == 0:
                groups = result['groups_detail']
                if len(groups)==0:
                    msg='公众号"%s"下的微信小店还没有商品分组，无需同步' % self.wx_officialaccount.wx_name
                    raise except_osv(_('提示'), _(msg))
                else:
                    for group in groups:
                        values = {}
                        values['wx_officialaccount'] = self.wx_officialaccount.id
                        values['wx_group_id'] = group['group_id']
                        values['wx_group_name'] = group['group_name']

                        exist_samename_groups = wx_productgroup_obj.search([('wx_group_name', '=', values['wx_group_name']),
                                                                            ('wx_officialaccount', '=',
                                                                             self.wx_officialaccount.id)])
                        if len(exist_samename_groups) > 0:
                            exist_samename_groups[0].write(values)
                        else:
                            wx_productgroup_obj.create(values)
            else:
                err_msg="调用微信小店获取所有分组接口失败:%s" % result['errmsg']
                _logger.info(err_msg)
                raise except_osv(_('错误'), _(err_msg))
        except Exception as e:
            err_msg=e.message
            if hasattr(e,'value'):
                err_msg+=e.value
            _logger.error(err_msg)
            raise except_osv(_('提示'), _(err_msg))