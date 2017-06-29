# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Expense',
    'version': '1.0',
    'category' : 'Hidden',
    'summary': 'Quotation, Sale Orders, Delivery & Invoicing Control',
    'description': """
Module used for demo data
=========================

Create some products for which you can re-invoice the costs.
This module does not add any feature, despite a few demo data to
test the features easily.
""",
    'author': '北京山水物源科技有限公司.',
    'website': 'http://www.yuancloud.cn/page/scm',
    'depends': ['sale', 'hr_expense'],
    'data': [
        'views/product_view.xml',
    ],
    'demo': ['sale_expense_demo.xml'],
    'test': [],
    'installable': True,
    'auto_install': True,
}
