# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.
{
    'name': 'Turkey - Accounting',
    'version': '1.0',
    'category' : 'Finance Management',
    'description': """
Türkiye için Tek düzen hesap planı şablonu YuanCloud Modülü.
==========================================================

Bu modül kurulduktan sonra, Muhasebe yapılandırma sihirbazı çalışır
    * Sihirbaz sizden hesap planı şablonu, planın kurulacağı şirket, banka hesap
      bilgileriniz, ilgili para birimi gibi bilgiler isteyecek.
    """,
    'author': 'Ahmet Altınışık',
    'maintainer':'https://launchpad.net/~yuancloud-turkey',
    'website':'https://launchpad.net/yuancloud-turkey',
    'depends': [
        'account',
        'base_vat',
    ],
    'data': [
        'account_tdhp_turkey.xml',
        'account_tax_template.xml',
        'account_chart_template.yml',
    ],
    'demo': [],
    'installable': True,
}
