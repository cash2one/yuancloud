{
    'name': 'eCommerce Optional Products',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'version': '1.0',
    'website': 'http://www.yuancloud.cn/page/e-commerce',
    'description': """
YuanCloud E-Commerce
==================

        """,
    'depends': ['website_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
