{
    'name' : 'YuanCloud Live Support',
    'version': '1.0',
    'summary': 'Chat with the YuanCloud collaborators',
    'category' : 'Tools',
    'complexity': 'medium',
    'website': 'http://www.yuancloud.cn/',
    'description':
        """
YuanCloud Live Support
=================

Ask your functional question directly to the YuanCloud Operators with the livechat support.

        """,
    'data': [
        "views/im_yuancloud_support.xml"
    ],
    'depends' : ["web", "mail"],
    'qweb': [
        'static/src/xml/im_yuancloud_support.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
