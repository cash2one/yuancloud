# -*- coding: utf-8 -*-
{
    'name': "Company -> Social Media Ids",

    'summary': """
        Display you company social medial contacts in your reports""",

    'description': """
        This modules adds the fields for social media IDs for the company. facebook Id, Twitter Handle and Google-Plus Id. These Ids can then be dispalyed in the reports such as invoice, payslips etc
    """,
    'images': ['static/description/social.png'],
#    'price': 2,
#    'currency': 'EUR',
    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category' : 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_company.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
