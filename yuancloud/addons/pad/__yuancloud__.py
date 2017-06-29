# -*- coding: utf-8 -*-
{
    'name': 'Collaborative Pads',
    'version': '2.0',
     'category' : 'Office Automation',#ԭ����Project Management
    'description': """
Adds enhanced support for (Ether)Pad attachments in the web client.
===================================================================

Lets the company customize which Pad installation should be used to link to new
pads (by default, http://etherpad.com/).
    """,
    'website': 'http://www.yuancloud.cn/page/notes',
    'depends': ['web'],
    'data': [
        'res_company.xml',
        'views/pad.xml',
    ],
    'demo': ['pad_demo.xml'],
    'installable': True,
    'auto_install': False,
    'web': True,
    'qweb' : ['static/src/xml/*.xml'],
}
