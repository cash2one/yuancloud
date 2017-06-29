# -*- encoding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Uruguay - Chart of Accounts',
    'version': '0.1',
    'author': 'Uruguay l10n Team & Guillem Barba',
    'category' : 'Finance Management',
    'website': 'https://launchpad.net/yuancloud-uruguay',
    'description': """
General Chart of Accounts.
==========================

Provide Templates for Chart of Accounts, Taxes for Uruguay.

""",
    'depends': ['account'],
    'data': [
        'account_chart_template.xml',
        'taxes_template.xml',
        'account_chart_template.yml',
    ],
    'demo': [],
    'installable': True,
}
