{
    'name': 'Resellers',
    'category' : 'Content Management',#ԭ����'Website',
    'website': 'http://www.yuancloud.cn/page/website-builder',
    'summary': 'Publish Your Channel of Resellers',
    'version': '1.0',
    'description': """
Publish and Assign Partner
==========================
        """,
    'depends': ['crm_partner_assign','website_partner', 'website_google_map'],
    'data': [
        'views/partner_grade.xml',
        'views/website_crm_partner_assign.xml',
    ],
    'demo': [
        'data/res_partner_grade_demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
