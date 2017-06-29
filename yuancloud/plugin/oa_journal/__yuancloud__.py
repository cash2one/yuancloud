# -*- coding: utf-8 -*-
{
    'name': "日常流水",

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
    'category' : 'Office Automation',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','product','hr_expense'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/ec_platform.xml',
        'data/invoice_type.xml',
        'data/journal_sequence.xml',
        'data/journal_workflow.xml',
        'views/invoice_type_view.xml',
        'views/ec_platform_view.xml',
        'views/journal_view.xml',
        'report/journal_report_view.xml',
        'journal_menu.xml',
        'security/menu_access.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'application': True,
}