# -*- coding: utf-8 -*-
{
    'name': "托管模式",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        Long description of module's purpose
    """,

    'author': "yinx@sswyuan.com",
    'website': "http://www.yuancloud.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','wx_platform','wx_message'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}