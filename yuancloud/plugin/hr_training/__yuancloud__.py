# -*- coding: utf-8 -*-
{
    'name': "培训管理",

    'summary': """
        培训管理""",

    'description': """
        Long description of module's purpose
    """,

    'author': "zhangzs@sswy.com",
    'website': "http://www.yuancloud.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/lession_view.xml',
        'views/record_view.xml',
        'views/employee_view.xml',
        'training_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}