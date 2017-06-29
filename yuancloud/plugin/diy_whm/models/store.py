# -*- coding: utf-8 -*-
from yuancloud import models, tools, fields, api, _
from yuancloud.osv.osv import except_osv

def _province_get(obj, cr, uid, context=None):
    '''
    省份默认：河北省
    :param obj:
    :param cr:
    :param uid:
    :param context:
    :return:
    '''
    if context is None:
        context = {}
    ids = obj.pool.get('res.country.state').search(cr, uid, [('code', '=', '冀')], context=context)
    if ids:
        # return ids[0]
        return obj.pool.get('res.country.state').browse(cr, uid, ids[0], context=context)
    return False

class store_extend(models.Model):
    '''
    功能：门店扩展
    '''
    _inherit = 'o2o.store'
    #库位更改为非必输
    virtual_location=fields.Many2one('stock.location', required=False,string='库位')
    #省份及城市增加默认
    province=fields.Many2one('res.country.state', required=True, string="省份",default=lambda self: _province_get(self, self.env.cr, self.env.user.id))
    city=fields.Char(required=True, string="城市",default='衡水')
    #营业时间更改为不必须输入
    business_hours=fields.Char(required=False, string='营业时间')
    #手机号更改为必输入
    mobile=fields.Char(required=False, string='手机号')
    #增加门店简称
    simple_name=fields.Char(string='门店简称')

    category=fields.Many2one('o2o.storecategory', required=False, string="门店类别")
    simple_info=fields.Text(required=False, string="简介")
    business_hours=fields.Char(required=False, string='营业时间')
    address=fields.Char(required=False, string="详细地址")

    # @api.model
    # def create(self, vals):
    #     '''
    #     重载：电话和手机号不能同时为空
    #     :param vals:
    #     :return:
    #     '''
    #     phone=vals.get('phone',False)
    #     mobile=vals.get('mobile',False)
    #     if not phone and not mobile:
    #         msg='电话和手机号不能同时为空'
    #         raise  except_osv(_('错误'), _(msg))
    #     else:
    #         return  super(store_extend, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     for store in self:
    #         phone=vals.get('phone',False)
    #         mobile=vals.get('mobile',False)
    #         if not phone and not mobile:
    #             msg='电话和手机号不能同时为空'
    #             raise  except_osv(_('错误'), _(msg))
    #         else:
    #             return super(store_extend, store).write(vals)

    def search_store(self,**kwargs):
        '''
        功能：重写消息事件中的search_store方法
        :param kwargs:
        :return:
        '''
        print kwargs
        store_str=kwargs['store_str']
        result=[]
        store_infos=self.env['o2o.store'].search(['|',('name','like',store_str),('simple_name','like',store_str)])
        if store_infos:
            if len(store_infos) < 8:
                for store_info in store_infos:
                    result.append(store_info)
                print result
                return result
            else:
                return [{'name':store_str,'address':False}]
        else:
            return [{'name':False}]
