# -*- coding: utf-8 -*-

# from yuanclound import models, fields, api

import itertools
from lxml import etree
import urllib2
import logging

try:
    import simplejson as json
except ImportError:
    import json

from yuancloud import models, fields, api, _
from yuancloud.exceptions import except_orm, Warning, RedirectWarning
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
from yuancloud.osv.osv import osv
import struct
import os
import time
from yuancloud.api import Environment

_logger = logging.getLogger(__name__)


class wx_officialaccount_menu(models.Model):

    _name = 'wx.officialaccount_menu'
    _description = "Ycloud Wechat OfficialAccount Menu"
    _rec_name = 'wx_menu_name'

    wx_menu_name=fields.Char('菜单名称', required=True)
    wx_menu_type= fields.Selection([('click', 'click'), ('view', 'view'),('scancode_push', 'scancode_push'),('scancode_waitmsg', 'scancode_waitmsg'),('pic_sysphoto', 'pic_sysphoto'),('pic_photo_or_album', 'pic_photo_or_album'),('pic_weixin', 'pic_weixin'),('location_select', 'location_select')], string="菜单类型")
    wx_menu_url=fields.Char('菜单关键字',required=True)
    wx_menu_level=fields.Selection([('one', '一级菜单'), ('two', '二级菜单')],required=True,string="菜单等级")
    sequence=fields.Integer('序列')
    parent_id=fields.Many2one('wx.officialaccount_menu', '父菜单', select=True, ondelete="cascade")
    child_id=fields.One2many('wx.officialaccount_menu', 'parent_id', string='Child Menus')
    officialaccount=fields.Many2one("wx.officialaccount",'微信公众号')
    officialaccount_menu_type=fields.Many2one("wx.officialaccount_menutype","菜单类型")

    def __defaults_sequence(self, cr, uid, context):
        menu = self.search_read(cr, uid, [(1, "=", 1)], ["sequence"], limit=1, order="sequence DESC", context=context)
        return menu and menu[0]["sequence"] or 0

    _defaults = {
        'wx_menu_type': 'click',
        'wx_menu_url': '',
        'sequence': __defaults_sequence,
        'officialaccount_menu_type':"",
    }

    # would be better to take a menu_id as argument
    def get_tree(self, cr, uid, website_id, context=None):
        def make_tree(node):
            menu_node = dict(
                id=node.id,
                wx_menu_name=node.wx_menu_name,
                wx_menu_type=node.wx_menu_type,
                wx_menu_url=node.wx_menu_url,
                sequence=node.sequence,
                parent_id=node.parent_id.id,
                children=[],
            )
            for child in node.child_id:
                menu_node['children'].append(make_tree(child))
            return menu_node

        menu = self.pool.get('wx.officialaccount_menu').browse(cr, uid, website_id, context=context).menu_id
        return make_tree(menu)

    def save(self, cr, uid, website_id, data, context=None):
        def replace_id(old_id, new_id):
            for menu in data['data']:
                if menu['id'] == old_id:
                    menu['id'] = new_id
                if menu['parent_id'] == old_id:
                    menu['parent_id'] = new_id
        to_delete = data['to_delete']
        if to_delete:
            self.unlink(cr, uid, to_delete, context=context)
        for menu in data['data']:
            mid = menu['id']
            if isinstance(mid, str):
                new_id = self.create(cr, uid, {'name': menu['name']}, context=context)
                replace_id(mid, new_id)
        for menu in data['data']:
            self.write(cr, uid, [menu['id']], menu, context=context)
        return True

    def get_officialaccount_menu(self,cr,uid,official_account_id,context=None):
        #env = Environment(cr,uid,context)
        print official_account_id
        root_domain = [('parent_id', '=', False),('officialaccount',"=",official_account_id),('officialaccount_menu_type','=',False)]
        menus = self.pool.get('wx.officialaccount_menu').search(cr,uid,root_domain,limit=3,order='sequence',context=context)
        menudata='''{"button": ['''
        for menu_id in menus:
            tmp_menu=self.pool.get('wx.officialaccount_menu').browse(cr,uid,menu_id,context)
            print tmp_menu
            menudata=menudata+'''{"name":"'''+tmp_menu["wx_menu_name"]+'''",'''
            sub_domain=[('parent_id', '=', tmp_menu['id']),('officialaccount',"=",official_account_id),('officialaccount_menu_type','=',False)]
            sub_menu_ids = self.pool.get('wx.officialaccount_menu').search(cr,uid,sub_domain,limit=5,order='sequence',context=context)
            if len(sub_menu_ids)>0:
                menudata=menudata+'''"sub_button":['''
                sub_menu_data=""
                for sub_menu_id in sub_menu_ids:
                    sub_menu=self.pool.get('wx.officialaccount_menu').browse(cr,uid,sub_menu_id,context)
                    sub_menu_data=sub_menu_data+'''{"name":"'''+sub_menu['wx_menu_name']+'''",'''
                    if sub_menu["wx_menu_type"]=="click":
                        sub_menu_data=sub_menu_data+'''"type":"click","key":"'''+sub_menu["wx_menu_url"]+'''"},'''
                    elif sub_menu["wx_menu_type"]=="view":
                        sub_menu_data=sub_menu_data+'''"type":"view","url":"'''+sub_menu["wx_menu_url"]+'''"},'''
                    elif sub_menu["wx_menu_type"]=="scancode_push":
                        sub_menu_data=sub_menu_data+'''"type":"scancode_push","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="scancode_waitmsg":
                        sub_menu_data=sub_menu_data+'''"type":"scancode_waitmsg","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_sysphoto":
                        sub_menu_data=sub_menu_data+'''"type":"pic_sysphoto","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_photo_or_album":
                        sub_menu_data=sub_menu_data+'''"type":"pic_photo_or_album","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_weixin":
                        sub_menu_data=sub_menu_data+'''"type":"pic_weixin","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="location_select":
                        sub_menu_data=sub_menu_data+'''"type":"location_select","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    #elif sub_menu["wx_menu_type"]=="media_id":
                    #    sub_menu_data=sub_menu_data+'''"type":"media_id","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    #elif sub_menu["wx_menu_type"]=="view_limited":
                    #    sub_menu_data=sub_menu_data+'''"type":"view_limited","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                menudata=menudata+sub_menu_data[:-1]+"]},"
            else:
                if tmp_menu["wx_menu_type"]=="click":
                    menudata=menudata+'''"type":"click","key":"'''+tmp_menu["wx_menu_url"]+'''"},'''
                elif tmp_menu["wx_menu_type"]=="view":
                    menudata=menudata+'''"type":"view","url":"'''+tmp_menu["wx_menu_url"]+'''"},'''
                elif tmp_menu["wx_menu_type"]=="scancode_push":
                    menudata=menudata+'''"type":"scancode_push","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="scancode_waitmsg":
                    menudata=menudata+'''"type":"scancode_waitmsg","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_sysphoto":
                    menudata=menudata+'''"type":"pic_sysphoto","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_photo_or_album":
                    menudata=menudata+'''"type":"pic_photo_or_album","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_weixin":
                    menudata=menudata+'''"type":"pic_weixin","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="location_select":
                    menudata=menudata+'''"type":"location_select","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                #elif sub_menu["wx_menu_type"]=="media_id":
                #    sub_menu_data=sub_menu_data+'''"type":"media_id","key":"'''+sub_menu["wx_menu_url"]+'''",},'''
                #elif sub_menu["wx_menu_type"]=="view_limited":
                #    sub_menu_data=sub_menu_data+'''"type":"view_limited","key":"'''+sub_menu["wx_menu_url"]+'''",},'''
        menudata=menudata[:-1]+"]}"
        _logger.debug(menudata)
        return menudata

    def get_custom_menu(self,cr,uid,context,code,official_account_id):
        print official_account_id
        env = Environment(cr,uid,context)
        root_domain = [('parent_id', '=', False),('officialaccount',"=",official_account_id),('officialaccount_menu_type','=',code)]
        menus = env['wx.officialaccount_menu'].search(root_domain,limit=3,order='sequence')
        menudata='''"button": ['''
        for menu_id in menus:
            #tmp_menu=env['wx.officialaccount_menu'].browse(menu_id)
            tmp_menu=menu_id
            print tmp_menu
            menudata=menudata+'''{"name":"'''+tmp_menu["wx_menu_name"]+'''",'''
            sub_domain=[('parent_id', '=', tmp_menu['id']),('officialaccount',"=",official_account_id),('officialaccount_menu_type','=',code)]
            sub_menu_ids =env['wx.officialaccount_menu'].search(sub_domain,limit=5,order='sequence')
            if len(sub_menu_ids)>0:
                menudata=menudata+'''"sub_button":['''
                sub_menu_data=""
                for sub_menu_id in sub_menu_ids:
                    sub_menu=sub_menu_id#env['wx.officialaccount_menu'].browse(sub_menu_id)
                    sub_menu_data=sub_menu_data+'''{"name":"'''+sub_menu['wx_menu_name']+'''",'''
                    if sub_menu["wx_menu_type"]=="click":
                        sub_menu_data=sub_menu_data+'''"type":"click","key":"'''+sub_menu["wx_menu_url"]+'''"},'''
                    elif sub_menu["wx_menu_type"]=="view":
                        sub_menu_data=sub_menu_data+'''"type":"view","url":"'''+sub_menu["wx_menu_url"]+'''"},'''
                    elif sub_menu["wx_menu_type"]=="scancode_push":
                        sub_menu_data=sub_menu_data+'''"type":"scancode_push","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="scancode_waitmsg":
                        sub_menu_data=sub_menu_data+'''"type":"scancode_waitmsg","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_sysphoto":
                        sub_menu_data=sub_menu_data+'''"type":"pic_sysphoto","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_photo_or_album":
                        sub_menu_data=sub_menu_data+'''"type":"pic_photo_or_album","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="pic_weixin":
                        sub_menu_data=sub_menu_data+'''"type":"pic_weixin","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                    elif sub_menu["wx_menu_type"]=="location_select":
                        sub_menu_data=sub_menu_data+'''"type":"location_select","key":"'''+sub_menu["wx_menu_url"]+'''","sub_button": [ ]},'''
                menudata=menudata+sub_menu_data[:-1]+"]},"
            else:
                if tmp_menu["wx_menu_type"]=="click":
                    menudata=menudata+'''"type":"click","key":"'''+tmp_menu["wx_menu_url"]+'''"},'''
                elif tmp_menu["wx_menu_type"]=="view":
                    menudata=menudata+'''"type":"view","url":"'''+tmp_menu["wx_menu_url"]+'''"},'''
                elif tmp_menu["wx_menu_type"]=="scancode_push":
                    menudata=menudata+'''"type":"scancode_push","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="scancode_waitmsg":
                    menudata=menudata+'''"type":"scancode_waitmsg","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_sysphoto":
                    menudata=menudata+'''"type":"pic_sysphoto","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_photo_or_album":
                    menudata=menudata+'''"type":"pic_photo_or_album","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="pic_weixin":
                    menudata=menudata+'''"type":"pic_weixin","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
                elif tmp_menu["wx_menu_type"]=="location_select":
                    menudata=menudata+'''"type":"location_select","key":"'''+tmp_menu["wx_menu_url"]+'''",},'''
        if menudata.endswith(","):
            menudata=menudata[:-1]+"]"
        else:
            menudata=menudata+"]"
        _logger.debug(menudata)
        return menudata

# 3.微信企业号应用,扩展微信服务号
class wx_qyh_app_menu(models.Model):
    _inherit = 'wx.officialaccount_menu'
    is_qyhapp = fields.Boolean(related='officialaccount.is_qyhapp', string='是否企业号应用')



