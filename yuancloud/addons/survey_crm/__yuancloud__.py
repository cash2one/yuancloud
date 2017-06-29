# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'Survey CRM',
    'version': '2.0',
    'category' : 'Sales Management',#ԭ����'Marketing'
    'complexity': 'easy',
    'website': 'http://www.yuancloud.cn/page/survey',
    'description': """
Survey - CRM (bridge module)
=================================================================================
This module adds a Survey mass mailing button inside the more option of lead/customers views
""",
    'depends': ['crm', 'survey'],
    'data': [
        'crm_view.xml',
    ],
    'installable': True,
    'auto_install': True
}
