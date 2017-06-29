# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale - Secondary UoM',
    'version': '1.0',
    'category' : 'Sales Management',
    'sequence': 14,
    'summary': 'Unit of Sale',
    'description': """
Manage secondary units of sale
==============================

Sell products in one unit of measure that is different from the one
you manage the inventory.
    """,
    'author': 'YuanCloud',
    'website': 'http://www.yuancloud.cn',
    'depends': ['sale'],
    'data': [
        'views/product_uos_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
