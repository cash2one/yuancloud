# -*- coding: utf-8 -*-
{
    'name': "wx_shop",

    'summary': """微信小店
        """,

    'description': """
        微信小店
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','wx_platform','product','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/wx_product_wf.xml',
        'views/wx_shop_view.xml',
        'views/wx_product_view.xml',
        'views/product_category_view.xml',
        'views/product_group_view.xml',
        'views/sync_group_view.xml',
        'views/wx_shop_order_view.xml',
        'views/sync_order_view.xml',
        # 'views/wx_carrier_view.xml',
        'wx_shop_menu.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}