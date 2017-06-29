# -*- coding: utf-8 -*-
# Part of YuanCloud. See LICENSE file for full copyright and licensing details.

{
    'name': 'Blogs',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'sequence': 140,
    'website': 'http://www.yuancloud.cn/page/cms',
    'summary': 'News, Blogs, Announces, Discussions',
    'version': '1.0',
    'description': """
YuanCloud Blog
============

        """,
    'depends': ['website_mail', 'website_partner'],
    'data': [
        'data/website_blog_data.xml',
        'views/website_blog_views.xml',
        'views/website_blog_templates.xml',
        'views/snippets.xml',
        'security/ir.model.access.csv',
        'security/website_blog.xml',
    ],
    'demo': [
        'data/website_blog_demo.xml'
    ],
    'test': [
        'tests/test_website_blog.yml'
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
}
