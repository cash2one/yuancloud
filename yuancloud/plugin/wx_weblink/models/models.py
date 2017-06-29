# -*- coding: utf-8 -*-
import datetime
from yuancloud import models, fields, api
from urlparse import urlparse
from urllib import urlencode
from yuancloud.osv import orm
from yuancloud.http import request
import logging
from yuancloud import SUPERUSER_ID
try:
    import simplejson as json
except ImportError:
    import json
from yuancloud.api import Environment

_logger = logging.getLogger(__name__)


class weblink(models.Model):
    _inherit = 'link.tracker'

    @api.model
    def _get_default_team(self):
        default_team_id = self.env['crm.team']._get_default_team_id()
        return self.env['crm.team'].browse(default_team_id)

    share_desc = fields.Char('描述')
    share_image = fields.Binary('分享图标')
    officialaccount = fields.Many2one('wx.officialaccount', '微信服务号/企业号', domain=[('is_qyhapp', '=', False)])
    qy_officialaccount = fields.Many2one('wx.officialaccount', '批量推送启用应用', domain=[('is_qyhapp', '=', True)])
    user_id = fields.Many2one('res.users', string='销售员', default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', '销售团队', default=_get_default_team)
    share_count = fields.Integer('微信分享量', compute='_compute_sharecount', store=True)
    link_share_ids = fields.One2many('link.tracker.share', 'link_id', string='分享')
    share_mood_1=fields.Text(string='分享朋友圈心情1')
    share_mood_2=fields.Text(string='分享朋友圈心情2')
    share_mood_3=fields.Text(string='分享朋友圈心情3')

    @api.one
    @api.depends('link_share_ids.link_id')
    def _compute_sharecount(self):
        self.share_count = len(self.link_share_ids)

    @api.multi
    def action_view_share_statistics(self):
        action = self.env['ir.actions.act_window'].for_xml_id('wx_weblink', 'action_view_share_statistics')
        action['domain'] = [('link_id', '=', self.id)]
        return action

    @api.multi
    def action_view_batchshare(self):
        print self
        self = self.sudo()
        link_trackers=self.env['link.tracker'].search([('user_id', '<>', False),('user_id.id','<>',0)])
        for link_tracker in link_trackers:
            link_info=self.env['link.tracker'].search([('user_id','=',link_tracker.user_id.id),('url','=',self.url)])
            if link_info:
                _logger.info('销售员已经点击过此链接')
            else:
                _logger.info("action_view_batchshare准备创建新数据")
                postdata = {}
                user=link_tracker.user_id
                title=(self.env['send_message'].replacecontent(self.title, {}, user, self._context))
                share_desc=(self.env['send_message'].replacecontent(self.share_desc, {}, user, self._context))
                postdata.update({
                    "url": self.url,
                    "title": title,
                    "share_desc": share_desc,
                    "share_image": self.share_image,
                    "user_id": link_tracker.user_id.id
                })
                if self.team_id:
                    postdata.update({
                        "team_id": self.team_id.id
                    })
                if self.officialaccount:
                    postdata.update({
                        "officialaccount": self.officialaccount.id
                    })
                if self.campaign_id:
                    postdata.update({
                        "campaign_id": self.campaign_id.id
                    })
                if self.medium_id:
                    postdata.update({
                        "medium_id": self.medium_id.id
                    })
                if self.source_id:
                    postdata.update({
                        "source_id": self.source_id.id
                    })
                if self.share_mood_1:
                    share_mood_1=(self.env['send_message'].replacecontent(self.share_mood_1, {}, user, self._context))
                    postdata.update({
                        "share_mood_1": share_mood_1
                    })
                if self.share_mood_2:
                    share_mood_2=(self.env['send_message'].replacecontent(self.share_mood_2, {}, user, self._context))
                    postdata.update({
                        "share_mood_2": share_mood_2
                    })
                if self.share_mood_3:
                    share_mood_3=(self.env['send_message'].replacecontent(self.share_mood_3, {}, user, self._context))
                    postdata.update({
                        "share_mood_3": share_mood_3
                    })
                _logger.info("data1")
                #_logger.info("data:" + json.dumps(postdata))
                _logger.info("data2")
                data = self.sudo().create(postdata).read()
                print data
                _logger.info("action_view_batchshare创建方法调用完成")
                self._cr.commit()
                link=self.env['link.tracker'].search([('user_id','=',link_tracker.user_id.id),('url','=',self.url)])
                result = []
                result.append(link)
                context=self._context.copy()
                openid = link_tracker.user_id.login
                context.update({
                        "openid":openid
                    })
                ir_model = self.env['ir.model'].search( [("model", '=', 'link.tracker')])
                model_instances = []
                for model_value in result:
                    model_instance = {}
                    model_instance.update({
                        "id": ir_model.id,
                        "model_value": model_value
                            })
                    model_instances.append(model_instance)
                env = Environment(self._cr, SUPERUSER_ID, context)
                send_event = 'wx.message.send_event'
                if send_event in self.env.registry:
                    env['wx.message.send_event'].sendmessage_TriggeredbyCommand('批量发送',model_instances,self.qy_officialaccount)
                else:
                    raise '未安装微信消息模块'

    @api.one
    @api.depends('url')
    def _compute_redirected_url(self):
        parsed = urlparse(self.url)

        utms = {}
        # for key, field, cook in self.env['utm.mixin'].tracking_fields():
        #     attr = getattr(self, field).id
        #     if attr:
        #         utms[key] = attr
        utms['redirect'] = self.short_url
        utms['code'] = self.code

        self.redirected_url = '%s://%s%s?%s&%s#%s' % (
        parsed.scheme, parsed.netloc, parsed.path, urlencode(utms), parsed.query, parsed.fragment)

    def search_link(self, **kwargs):
        print kwargs
        sale_id = kwargs['user_id']
        offset = kwargs.get('offset', 0)
        try:
            offset = (int)(offset)
        except:
            offset = 0
        _logger.info("sale_id:" + sale_id)
        user = self.env['res.users'].sudo().search([('login', '=', sale_id)])
        if not user:
            _logger.info("不存在此用户")
            return []
        links = self.sudo().search([('user_id', '=', False)])
        _logger.info("未维护销售员的link数量:" + str(len(links)))
        for link in links:
            link_new = self.sudo().search([('url', '=', link.url), ('user_id', '=', user.id)])
            if link_new:
                pass
            else:
                _logger.info("准备创建新数据")
                postdata = {}
                title=(self.env['send_message'].replacecontent(link.title, {}, user, self._context))
                share_desc=(self.env['send_message'].replacecontent(link.share_desc, {}, user, self._context))
                postdata.update({
                    "url": link.url,
                    "title": title,
                    "share_desc": share_desc,
                    "share_image": link.share_image,
                    "user_id": user.id
                })
                if link.team_id:
                    postdata.update({
                        "team_id": link.team_id.id
                    })
                if link.officialaccount:
                    postdata.update({
                        "officialaccount": link.officialaccount.id
                    })
                if link.campaign_id:
                    postdata.update({
                        "campaign_id": link.campaign_id.id
                    })
                if link.medium_id:
                    postdata.update({
                        "medium_id": link.medium_id.id
                    })
                if link.source_id:
                    postdata.update({
                        "source_id": link.source_id.id
                    })
                if link.share_mood_1:
                    share_mood_1=(self.env['send_message'].replacecontent(link.share_mood_1, {}, user, self._context))
                    postdata.update({
                        "share_mood_1": share_mood_1
                    })
                if link.share_mood_2:
                    share_mood_2=(self.env['send_message'].replacecontent(link.share_mood_2, {}, user, self._context))
                    postdata.update({
                        "share_mood_2": share_mood_2
                    })
                if link.share_mood_3:
                    share_mood_3=(self.env['send_message'].replacecontent(link.share_mood_3, {}, user, self._context))
                    postdata.update({
                        "share_mood_3": share_mood_3
                    })
                _logger.info("data1")
                #_logger.info("data:" + json.dumps(postdata))
                _logger.info("data2")
                data = self.sudo().create(postdata).read()
                print data
                _logger.info("创建方法调用完成")
                self._cr.commit()
        links = self.sudo().search([('user_id', '=', sale_id)],order='create_date DESC', limit=8, offset=offset)
        result = []
        if links:
            _logger.info("总数量:" + str(len(links)))
            for orderinfo in links:
                result.append(orderinfo)
            print result
            return result
        else:
            return []


class weblink_mixin(models.AbstractModel):
    _inherit = ['utm.mixin']

    officialaccount = fields.Many2one('wx.officialaccount', 'officialaccount')
    user_id = fields.Many2one('res.users', 'user_id')
    team_id = fields.Many2one('crm.team', 'team_id')

    def tracking_fields(self):
        return [
            # ("URL_PARAMETER", "FIELD_NAME_MIXIN", "NAME_IN_COOKIES")
            ('utm_campaign', 'campaign_id', 'yuancloud_utm_campaign'),
            ('utm_source', 'source_id', 'yuancloud_utm_source'),
            ('utm_medium', 'medium_id', 'yuancloud_utm_medium'),
            ('officialaccount', 'officialaccount', 'officialaccount'),
            ('user_id', 'user_id', 'user_id'),
            ('team_id', 'team_id', 'team_id')
        ]


class link_tracker_share(models.Model):
    _name = "link.tracker.share"
    _rec_name = "link_id"

    share_date = fields.Date(string='Share Date')
    link_id = fields.Many2one('link.tracker', 'Link', required=True, ondelete='cascade')
    ip = fields.Char(string='Internet Protocol')
    country_id = fields.Many2one('res.country', 'Country')

    @api.model
    def add_click(self, code, ip, country_code, stat_id=False):
        self = self.sudo()
        code_rec = self.env['link.tracker.code'].search([('code', '=', code)])

        if not code_rec:
            return None

        again = self.search_count([('link_id', '=', code_rec.link_id.id), ('ip', '=', ip)])

        if not again:
            country_record = self.env['res.country'].search([('code', '=', country_code)], limit=1)

            vals = {
                'link_id': code_rec.link_id.id,
                'create_date': datetime.date.today(),
                'ip': ip,
                'country_id': country_record.id,
                'mail_stat_id': stat_id
            }

            if stat_id:
                mail_stat = self.env['mail.mail.statistics'].search([('id', '=', stat_id)])

                if mail_stat.mass_mailing_campaign_id:
                    vals['mass_mailing_campaign_id'] = mail_stat.mass_mailing_campaign_id.id

                if mail_stat.mass_mailing_id:
                    vals['mass_mailing_id'] = mail_stat.mass_mailing_id.id

            self.create(vals)

# class weblink_ir_http(orm.AbstractModel):
#     _inherit = 'ir.http'
#
#     def _dispatch(self):
#         response = super(weblink_ir_http, self)._dispatch()
#         for var, dummy, cook in self.pool['utm.mixin'].tracking_fields():
#             if var in request.params and request.httprequest.cookies.get(var) != request.params[var]:
#                 try:
#                     response.set_cookie(cook, request.params[var], domain=self.get_utm_domain_cookies())
#                 except:
#                     pass
#         return response
