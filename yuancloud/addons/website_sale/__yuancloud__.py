{
    'name': 'eCommerce',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'sequence': 55,
    'summary': 'Sell Your Products Online',
    'website': 'http://www.yuancloud.cn/page/e-commerce',
    'version': '1.0',
    'description': """
YuanCloud E-Commerce
==================

        """,
    'depends': ['website', 'sale', 'payment', 'website_payment', 'website_portal_sale', 'website_mail', 'rating'],
    'data': [
        'data/data.xml',
        'data/web_planner_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/payment.xml',
        'views/sale_order.xml',
        'views/snippets.xml',
        'views/report_shop_saleorder.xml',
        'res_config_view.xml',
        'security/ir.model.access.csv',
        'security/website_sale.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
}
