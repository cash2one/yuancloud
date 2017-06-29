# -*- coding: utf-8 -*-
from yuancloud.osv import osv
from yuancloud import api, fields, models
from yuancloud.http import request

class Website(models.Model):

    _inherit = "website"

    channel_id = fields.Many2one('im_livechat.channel', string='Website Live Chat Channel')


class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    channel_id = fields.Many2one('im_livechat.channel', string='Website Live Chat Channel', related='website_id.channel_id')
