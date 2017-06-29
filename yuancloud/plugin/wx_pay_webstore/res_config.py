# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

from yuancloud.osv import osv, fields

import logging
_logger = logging.getLogger(__name__)

class base_config_settings(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'website_wxpayment_enabled': fields.boolean('启用网站微信支付功能...'),
        'wx_officicalaccount':fields.many2one('wx.officialaccount',string="微信服务号",domain=[('is_qyhapp','=',False)]),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(base_config_settings, self).default_get(cr, uid, fields, context=context)
        res.update(self.get_wx_pay_providers(cr, uid, fields, context=context))
        return res

    def get_wx_pay_providers(self, cr, uid, fields, context=None):
        rg = self.pool.get('payment.acquirer').search(cr, uid, [('provider','=','weixin')],context=context)
        print rg
        if rg:
            acquirerinfo=self.pool.get('payment.acquirer').browse(cr,uid,rg,context)
            platform_id = self.pool.get('wx.officialaccount').search(cr, uid,
                                                                       [('id','=',acquirerinfo[0]['weixin_officialaccount'].id)],
                                                                       context=context)
            print platform_id
            if platform_id:
                return {
                    'website_wxpayment_enabled': acquirerinfo[0]['website_published'],
                    'wx_officicalaccount': platform_id[0],
                }
            else:
                return {
                    'website_wxpayment_enabled': acquirerinfo[0]['website_published'],
                    'wx_officicalaccount':False,
                }
        else:
            return {
                'website_wxpayment_enabled': False,
                'wx_officicalaccount':False,
            }

    def set_oauth_providers(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        print config
        rg = self.pool.get('payment.acquirer').search(cr, uid, [('provider','=','weixin')],context=context)
        data = {
            'website_published': config.website_wxpayment_enabled,
            'weixin_officialaccount': config.wx_officicalaccount.id,
        }
        print rg
        print data
        if rg:
            self.pool.get('payment.acquirer').write(cr, uid, rg, data)



class AccountPaymentConfig(osv.TransientModel):
    _inherit = 'account.config.settings'

    _columns = {
        'module_wx_pay_webstore': fields.boolean(
            'Weixin Website Payment',
            help='-It installs the module wx_pay_webstore.'),
     }
