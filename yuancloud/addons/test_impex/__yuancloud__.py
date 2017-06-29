# -*- coding: utf-8 -*-
{
    'name': 'test-import-export',
    'version': '0.1',
    'category': 'Hidden',
    'description': """A module to test import/export.""",
    'author': '北京山水物源科技有限公司.',
    'maintainer': '北京山水物源科技有限公司.',
    'website': 'http://www.yuancloud.cn',
    'depends': ['base'],
    'data': ['ir.model.access.csv'],
    'installable': True,
    'auto_install': False,
    'test': [
        'tests/test_import_reference.yml',
        'tests/test_import_menuitem.yml',
    ]
}
