{
    'name': 'eCommerce Delivery',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'summary': 'Add Delivery Costs to Online Sales',
    'website': 'http://www.yuancloud.cn/page/e-commerce',
    'version': '1.0',
    'description': """
Delivery Costs
==============
""",
    'depends': ['website_sale', 'delivery'],
    'data': [
        'views/website_sale_delivery.xml',
        'views/website_sale_delivery_view.xml',
        'security/ir.model.access.csv',
        'demo/website_sale_delivery_data.xml'
    ],
    'demo': [
        'data/website_sale_delivery_demo.xml'
    ],
    'qweb': [],
    'installable': True,
}
