# -*- coding: utf-8 -*-
{
    'name': "saas_sale",

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
    'category' : 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','saas_portal_demo','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/saas_portal_view.xml',
        'views/product_view.xml',
        'report/sale_report.xml',
        'report/report_saleorder.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}