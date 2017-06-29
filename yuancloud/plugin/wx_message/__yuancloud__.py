# -*- coding: utf-8 -*-
{
    'name': "wx_message",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.yuancloud.cn""",

    'description': """
        微信消息
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/yuancloud/yuancloud/blob/master/yuancloud/addons/base/module/module_data.xml
    # for the full list
    'category': 'Wechat',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','wx_platform','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'demo/wx_messagetype.xml',
        'views/message_template/wx_text_message_template.xml',
        'views/message_template/wx_mpnews_message_template.xml',
        'views/message_template/wx_notify_message_template.xml',
        'views/message_template/wx_image_message_template.xml',
        'views/message_template/wx_voice_message_template.xml',
        'views/message_template/wx_link_message_template.xml',
        'views/message_template/wx_location_message_template.xml',
        'views/message_template/wx_video_message_template.xml',
        'views/message_template/wx_music_message_template.xml',
        'views/message_template/wx_list_message_template.xml',
        'views/message_template/wx_message_send_event.xml',
        'views/message_record/wx_text_message_record.xml',
        'views/message_record/wx_mpnews_message_record.xml',
        'views/message_record/wx_notify_message_record.xml',
        'views/message_record/wx_image_message_record.xml',
        'views/message_record/wx_voice_message_record.xml',
        'views/message_record/wx_link_message_record.xml',
        'views/message_record/wx_location_message_record.xml',
        'views/message_record/wx_video_message_record.xml',
        'views/message_record/wx_music_message_record.xml',
        'message_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}