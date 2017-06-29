# -*- encoding: utf-8 -*-
{
    'name': 'Partner Authentication with Fiscal Document',
    'description': """
* Keep track of due legal identification of partners with a \
corresponing document.
* Register additional document types within the GUI.
* Easy hook for custom copy and validation/formatting methods \
(res_partner_document.py)
""",
    'category' : 'Hidden',
    'license': 'AGPL-3',
    'author': 'Juan Pablo Arias (devCO), David Arnold BA HSG (devCO)',
    'website': '',
    'version': '0.3',
    'depends': [
        'base',
        'l10n_co_razonsocial',
    ],
    'data': [
        'data/res.partner.idtype.csv',
        'res_partner_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
