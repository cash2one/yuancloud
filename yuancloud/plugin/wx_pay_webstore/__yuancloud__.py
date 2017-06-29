# -*- coding: utf-8 -*-
{
    'name': "wx_pay_webstore",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        电商支持微信支付
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','wx_base','payment','website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'res_config.xml',
        'views/payment_acquirer.xml',
        'views/weixin.xml',
        'data/weixin.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}