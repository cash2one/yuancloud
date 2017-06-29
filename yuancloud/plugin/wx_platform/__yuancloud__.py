# -*- coding: utf-8 -*-
{
    'name': "wx_platform",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        微信接入平台
    """,

    'author': "yinx@sswyuan.com",
    'website': "http://www.yuancloud.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','wx_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/base_apppartner.xml',
        'views/wx_qyh_extend.xml',
        'views/wx_officialaccount_extend.xml',
        'views/wx_customer.xml',
        'views/wx_officialaccount_menu.xml',
        'views/wx_qyhapp_menu.xml',
        'views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}