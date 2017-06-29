# -*- coding: utf-8 -*-
{
    'name': "diy_xyl_production",

    'summary': """
        鑫玉龙生产系统扩展
        """,
    'description': """
        Long description of module's purpose
    """,

    'author': "zhangzs@sswyuan.com",
    'website': "http://www.yuancloud.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp_operations'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/finish_plan_view.xml',
        'views/operation_work_view.xml',
        'views/mrp_view.xml',
        'views/stock_move_view.xml',
        'production_menu.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}