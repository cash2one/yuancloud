# -*- encoding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2009 P. Christeas <p_christ@hol.gr>. All Rights Reserved

{
    'name': 'Greece - Accounting',
    'version': '0.2',
    'author': 'P. Christeas, 北京山水物源科技有限公司..',
    'website': 'http://yuancloud.hellug.gr/',
    'category' : 'Finance Management',
    'description': """
This is the base module to manage the accounting chart for Greece.
==================================================================

Greek accounting chart and localization.
    """,
    'depends': ['base', 'account', 'base_iban', 'base_vat'],
    'demo': [],
    'data': [ 'account_types.xml',
               'account_full_chart.xml',
               'account_tax.xml',
               'account_tax_vat.xml',
               'account_chart_template.yml'
    ],
    'installable': True,
}
