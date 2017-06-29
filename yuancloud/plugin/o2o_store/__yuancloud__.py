# -*- coding: utf-8 -*-
{
    'name': "门店管理",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "zhangzs@sswyuan.com",
    'website': "http://www.sswyuan.net/yuancloud",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Offline 2 Online',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'crm', 'website','web_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # 注意先后顺序
        'views/store_category_view.xml',
        'views/store_view.xml',
        'views/sale_order_view.xml',
        'store_menu.xml',
        'views/templates.xml',

    ],
    "qweb": [
        'static/src/xml/store_templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
