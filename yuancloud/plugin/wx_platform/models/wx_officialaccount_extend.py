# -*- coding: utf-8 -*-
import yuancloud
from yuancloud import models, fields, api, _
from yuancloud.tools.translate import _
from yuancloud.osv.osv import except_osv
import json
from yuancloud.addons.wx_base.sdks.officalaccount_sdk import menu_manager
from yuancloud.addons.wx_base.sdks.openplatform_sdk import public_sdk
from yuancloud.addons.wx_base.sdks.enterpriseaccount_sdk import menu_manager as qyh_menu_manager

class wx_officalaccount_menutype(models.Model):

    _name = 'wx.officialaccount_menutype'
    _rec_name = "code"

    code=fields.Char(string="菜单编码")
    desc=fields.Char(string="菜单描述")
    sex=fields.Selection([('0', ''), ('1', '男'), ('2', '女')],string="性别")
    #group_id=fields.Many2one('ycloud.wx.customer_group',string="用户分组")
    #group_id=fields.Many2many('ycloud.wx.customer_group', 'menutype_customer_group_rel', 'menutype_id','groupid',string="用户分组")
    client_platform_type=fields.Selection([('1', 'IOS'), ('2', 'Android'), ('3', 'Others')],string="客户端版本")
    country=fields.Char(string="国家")
    province=fields.Char(string="省份")
    city=fields.Char(string="城市")
    officalaccount=fields.Many2one("wx.officialaccount",string="微信服务号")
    menuid=fields.Char(string="菜单ID",readonly=True)

    _defaults = {
        'code': 'default',
    }

    @api.one
    def create_custom_menu(self):
        print self
        code=self.code
        officalaccount=self.officalaccount.id
        if code:
            print code
            print officalaccount
            if self.menuid:
                raise except_osv(_('Error!'), _(u"已经创建微信个性化菜单,不能再次创建"))
            custom_menu=self.pool.get('wx.officialaccount_menu').get_custom_menu(self._cr,self._uid,self._context,code,officalaccount)
            print custom_menu
            matchrule={}
            if self.sex:
                matchrule.update({
                    "sex":self.sex
                })
            # if self.group_id:
            #     matchrule.update({
            #         "group_id":self.group_id['groupid']
            #     })
            if self.client_platform_type:
                matchrule.update({
                    "client_platform_type":self.client_platform_type
                })
            if self.country:
                matchrule.update({
                    "country":self.country
                })
            if self.province:
                matchrule.update({
                    "province":self.province
                })
            if self.city:
                matchrule.update({
                    "city":self.city
                })
            menudata="{"+custom_menu+","+"\"matchrule\":"+json.dumps(matchrule,ensure_ascii=False)+"}"
            print menudata
            if self.officalaccount.is_auth_officialaccount:
                auth_access_token=public_sdk.get_authorizer_access_token(self.officalaccount.wx_appid,self.officalaccount.auth_component.auth_component_appid,self.officalaccount.auth_component.auth_component_appsecret,self.officalaccount.authorizer_refresh_token)
                menuresult=menu_manager.create_addconditional_menu_access_token(menudata,auth_access_token)
                pass
            else:
                menuManager = menu_manager.menu_manager(self.officalaccount.wx_appid,self.officalaccount.wx_appsecret)
                menuresult = menuManager.create_addconditional_menu(menudata)
            if 'errcode' in menuresult:
                result="创建个性化菜单失败:"+str(menuresult['errcode'])+","+menuresult['errmsg']
                raise except_osv(_('Error!'), _(result))
                pass
            else:
                menuid=menuresult['menuid']
                self.menuid=menuid
            print menuresult

    @api.one
    def del_custom_menu(self):
        print self
        if self.menuid:
            if self.officalaccount.is_auth_officialaccount:
                auth_access_token=public_sdk.get_authorizer_access_token(self.officalaccount.wx_appid,self.officalaccount.auth_component.auth_component_appid,self.officalaccount.auth_component.auth_component_appsecret,self.officalaccount.authorizer_refresh_token)
                menuresult=menu_manager.delete_addconditonal_menu_access_token(self.menuid,auth_access_token)
                pass
            else:
                menuManager = menu_manager.menu_manager(self.officalaccount.wx_appid,self.officalaccount.wx_appsecret)
                menuresult = menuManager.delete_addconditional_menu(self.menuid)
            print menuresult
            if 'errcode' in menuresult:
                if menuresult['errcode']==0:
                    self.menuid=False
                    self._cr.commit()
                    raise except_osv(_('Info!'), _(u"删除个性化菜单成功"))
                else:
                    result="删除个性化菜单失败:"+str(menuresult['errcode'])+","+menuresult['errmsg']
                    raise except_osv(_('Error!'), _(result))
        else:
            raise except_osv(_('Error!'), _(u"未创建个性化菜单，不能删除!"))

class wx_officialaccount_extend(models.Model):
    _inherit = 'wx.officialaccount'

    wx_encodingasekey = fields.Char(string="消息加解密密钥")
    wx_apptoken = fields.Char('Token')
    wx_id = fields.Char(string="原始ID")
    operator_name = fields.Char(string="运营者姓名")
    register_mobile = fields.Char(string="手机号")
    register_email = fields.Char(string="邮箱")
    auth_time = fields.Date(string="认证时间")
    wx_number = fields.Char(string="微信号")
    cus_phone = fields.Char(string="客服电话")

    is_auth_officialaccount = fields.Boolean(string="是否授权应用")
    auth_component = fields.Many2one('wx.third_platform', string='第三方平台')
    authorizer_refresh_token = fields.Char("授权应用刷新令牌")

    open_store = fields.Boolean(string="是否开通微信门店")
    open_scan = fields.Boolean(string="是否开通微信扫一扫")
    open_pay = fields.Boolean(string="是否开通微信支付")
    open_card = fields.Boolean(string="是否开通微信卡劵")
    open_shake = fields.Boolean(string="是否开通微信摇一摇")

    service_type_info = fields.Selection([('0', '订阅号'), ('1', '升级后的订阅号'), ('2', '服务号')], string="公众号类型")
    verify_type_info = fields.Selection(
        [('-1', '未认证'), ('0', '微信认证'), ('1', '新浪微博认证'), ('2', '腾讯微博认证'), ('3', '已资质认证通过但还未通过名称认证'),
         ('4', '已资质认证通过、还未通过名称认证，但通过了新浪微博认证'), ('5', '已资质认证通过、还未通过名称认证，但通过了腾讯微博认证')], string="认证类型")
    location_report = fields.Selection([('0', '无上报'), ('1', '进入会话时上报'), ('2', '每5s上报')], string="地理位置上报选项")
    voice_recognize = fields.Selection([('0', '关闭语音识别'), ('1', '开启语音识别')], string="语音识别开关选项")
    customer_service = fields.Selection([('0', '关闭多客服'), ('1', '开启多客服')], string="多客服开关选项")

    third_auth_id = fields.Char(string="第三方授权方套件ID", readonly=True)
    third_auth_code = fields.Char(string="第三方永久授权码", readonly=True)

    wx_officalaccount_menutypes = fields.One2many('wx.officialaccount_menutype', 'officalaccount', '菜单类型')


    def getqyhofficialaccount(self,officalaccountid,agentid):
        wx_officialaccount_list = self.env['wx.officialaccount'].search([('wx_appid', '=', officalaccountid),('wx_qyh_app_id','=',agentid)])
        if not wx_officialaccount_list or len(wx_officialaccount_list) > 1:
            error_msg = 'official account: received data for reference %s' % (officalaccountid)
            if not wx_officialaccount_list:
                error_msg += '; no officialaccount found'
            else:
                error_msg += '; multiple officialaccount found'
            raise except_osv(error_msg)
        return wx_officialaccount_list[0]

    def getofficialaccount(self,officalaccountid):
        wx_officialaccount_list = self.env['wx.officialaccount'].search([('wx_id', '=', officalaccountid)])
        if not wx_officialaccount_list or len(wx_officialaccount_list) > 1:
            error_msg = 'official account: received data for reference %s' % (officalaccountid)
            if not wx_officialaccount_list:
                error_msg += '; no officialaccount found'
            else:
                error_msg += '; multiple officialaccount found'
            raise except_osv(error_msg)
        return wx_officialaccount_list[0]

    def create_menu(self, cr, uid, ids, context=None):
        count = len(ids)
        if count == 0:
            print 'count=0'
            return
        result_success = ""
        for id in ids:
            wxOfficeAccountInfo = self.browse(cr, uid, id, context)
            menu_data = self.pool.get('wx.officialaccount_menu').get_officialaccount_menu(cr, uid, id, context)
            if wxOfficeAccountInfo.is_qyhapp:
                #创建企业号菜单
                menuManager_qyh = qyh_menu_manager.menu_manager(wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['wx_appsecret'])
                menuresult_qyh = menuManager_qyh.create_menu(menu_data,str(wxOfficeAccountInfo['wx_qyh_app_id']))
                result_success = result_success + "应用:" + wxOfficeAccountInfo['wx_name'] + menuresult_qyh + ";"
            else:
                #创建服务号菜单
                # menu_data = self.pool.get('ycloud.wx.officialaccount_menu').get_officialaccount_menu(cr, uid, id, context)
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component.auth_component_appid,wxOfficeAccountInfo.auth_component.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    menuresult=menu_manager.create_menu_access_token(menu_data,auth_access_token)
                    pass
                else:
                    menuManager = menu_manager.menu_manager(wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['wx_appsecret'])
                    menuresult = menuManager.create_menu(menu_data)
                result_success = result_success + "公众号:" + wxOfficeAccountInfo['wx_name'] + menuresult + ";"
        result = result_success[:-1]
        raise except_osv(_('Warning!'), _(result))

    def delete_menu(self, cr, uid, ids, context=None):
        count = len(ids)
        if count == 0:
            print 'count=0'
            return
        result_success = ""
        for id in ids:
            wxOfficeAccountInfo = self.browse(cr, uid, id, context)
            if wxOfficeAccountInfo.is_qyhapp:
                #删除企业号菜单
                menuManager_qyh = qyh_menu_manager.menu_manager(wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['wx_appsecret'])
                menuresult_qyh = menuManager_qyh.delete_menu(str(wxOfficeAccountInfo['wx_qyh_app_id']))
                result_success = result_success + "应用:" + wxOfficeAccountInfo['wx_name'] + menuresult_qyh + ";"
                pass
            else:
                #删除服务号菜单
                if wxOfficeAccountInfo.is_auth_officialaccount:
                    auth_access_token=public_sdk.get_authorizer_access_token(wxOfficeAccountInfo.wx_appid,wxOfficeAccountInfo.auth_component.auth_component_appid,wxOfficeAccountInfo.auth_component.auth_component_appsecret,wxOfficeAccountInfo.authorizer_refresh_token)
                    menuresult=menu_manager.delete_menu_access_token(auth_access_token)
                    pass
                else:
                    menuManager = menu_manager.menu_manager(wxOfficeAccountInfo['wx_appid'],wxOfficeAccountInfo['wx_appsecret'])
                    menuresult = menuManager.delete_menu()
                result_success = result_success + "公众号:" + wxOfficeAccountInfo['wx_name'] + menuresult + ";"
        result = result_success[:-1]
        raise except_osv(_('Warning!'), _(result))

class wx_qyh_extend(models.Model):
    _inherit = "wx.qyh"
    operator_name = fields.Char(string="运营者姓名")
    register_mobile = fields.Char(string="手机号")
    register_email = fields.Char(string="邮箱")
    auth_time = fields.Date(string="认证时间")
    wx_number = fields.Char(string="微信号")
    cus_phone = fields.Char(string="客服电话")
