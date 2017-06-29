{
    'name': 'Web Calendar',
    'category' : 'Hidden',
    'description':"""
YuanCloud Web Calendar view.
==========================

""",
    'author': '北京山水物源科技有限公司., Valentino Lab (Kalysto)',
    'version': '2.0',
    'depends': ['web'],
    'data' : [
        'views/web_calendar.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True
}
