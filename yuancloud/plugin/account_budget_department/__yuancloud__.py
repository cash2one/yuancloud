# -*- coding: utf-8 -*-
{
    'name': "部门预算管理",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "zhangzs@sswyuan.com",
    'website': "http://www.yuancloud.cn/page/productline_fi",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category' : 'Finance Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_budget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_budget_view.xml',
        'views/account_account_view.xml',
        'views/account_analytic_view.xml',
    ],
}