# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.


{
    'name': 'ESC/POS Hardware Driver',
    'version': '1.0',
    'category' : 'Offline 2 Online', #‘≠∑÷¿‡ 'Hardware Drivers',
    'sequence': 6,
    'website': 'http://www.yuancloud.cn/page/point-of-sale',
    'summary': 'Hardware Driver for ESC/POS Printers and Cashdrawers',
    'description': """
ESC/POS Hardware Driver
=======================

This module allows yuancloud to print with ESC/POS compatible printers and
to open ESC/POS controlled cashdrawers in the point of sale and other modules
that would need such functionality.

""",
    'depends': ['hw_proxy'],
    'external_dependencies': {
        'python' : ['usb.core','serial','qrcode'],
    },
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
