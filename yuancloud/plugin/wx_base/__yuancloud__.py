# -*- coding: utf-8 -*-
{
    'name': "wx_base",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        微信基类，用于描述微信相关实体最小集
    """,

    'author': "yinx@sswyuan.com",
    'website': "http://www.yuancloud.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'res_config.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/wx_officialaccount.xml',
        'views/wx_officialaccount_webapp.xml',
        'views/wx_qyh.xml',
        'views/wx_third_platform.xml',
        'views/wx_qyhapp.xml',
        'views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}