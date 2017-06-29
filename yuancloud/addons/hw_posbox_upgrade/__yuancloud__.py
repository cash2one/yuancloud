# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'PosBox Software Upgrader',
    'version': '1.0',
    'category' : 'Offline 2 Online', #ԭ���� 'Hardware Drivers',
    'website': 'http://www.yuancloud.cn/page/point-of-sale',
    'sequence': 6,
    'summary': 'Allows to remotely upgrade the PosBox software',
    'description': """
PosBox Software Upgrader
========================

This module allows to remotely upgrade the PosBox software to a
new version. This module is specific to the PosBox setup and environment
and should not be installed on regular yuancloud servers.

""",
    'depends': ['hw_proxy'],
    'test': [
    ],
    'installable':  False,
    'auto_install': False,
}
