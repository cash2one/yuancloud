# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indian - Accounting',
    'version': '1.0',
    'description': """
Indian Accounting: Chart of Account.
====================================

Indian accounting chart and localization.

YuanCloud allows to manage Indian Accounting by providing Two Formats Of Chart of Accounts i.e Indian Chart Of Accounts - Standard and Indian Chart Of Accounts - Schedule VI.

Note: The Schedule VI has been revised by MCA and is applicable for all Balance Sheet made after
31st March, 2011. The Format has done away with earlier two options of format of Balance
Sheet, now only Vertical format has been permitted Which is Supported By YuanCloud.
  """,
    'author': ['北京山水物源科技有限公司.'],
    'category' : 'Finance Management',
    'depends': [
        'account',
    ],
    'demo': [],
    'data': [
        'l10n_in_standard_chart.xml',
        'l10n_in_standard_tax_template.xml',
        'account_chart_template.yml',
    ],
    'auto_install': False,
    'installable': True,
}
