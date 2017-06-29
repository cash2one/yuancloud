# -*- coding: utf-8 -*-
{
    'name': "微号码定制",

    'summary': """
        微号码定制
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
    'depends': ['base','o2o_store'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/store_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}