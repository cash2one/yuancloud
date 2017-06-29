# -*- coding: utf-8 -*-
from yuancloud.osv import fields, osv

class company_pad(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'pad_server': fields.char('Pad Server', help="Etherpad lite server. Example: beta.primarypad.com"),
        'pad_key': fields.char('Pad Api Key', help="Etherpad lite api key.", groups="base.group_system"),
    }
