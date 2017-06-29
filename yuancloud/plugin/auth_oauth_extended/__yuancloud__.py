# -*- coding: utf-8 -*-
{
    'name': "auth_oauth_extended",

    'summary': """
        for weixin authorization and login into Odoo """,

    'description': """
Allow users to login through OAuth2 Provider those in china.
=============================================================
Weixin
etc.

    """,

    'category' : 'Wechat',
    'version': '0.1',
    'author': "yinx@sswyuan.com",
    'website': "http://www.yuancloud.cn",
    'depends': ['auth_oauth','wx_base'],

    'data': [
        'security/ir.model.access.csv',
        'auth_oauth_view.xml',
        'auth_oauth_data.xml',
        'res_config.xml',
        'res_users_view.xml',
    ],

    'installable': True,

}