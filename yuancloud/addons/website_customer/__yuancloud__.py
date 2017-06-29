# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer References',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'website': 'http://www.yuancloud.cn/page/website-builder',
    'summary': 'Publish Your Customer References',
    'version': '1.0',
    'description': """
YuanCloud Customer References
===========================
""",
    'depends': [
        'crm_partner_assign',
        'website_partner',
        'website_google_map',
    ],
    'demo': [
        'website_customer_demo.xml',
    ],
    'data': [
        'views/website_customer.xml',
        'views/website_customer_view.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'qweb': [],
    'installable': True,
}
