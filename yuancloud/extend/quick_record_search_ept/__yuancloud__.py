{

 'name' : 'Quick Record Search',
 'version' : '1.0.0',
 'author' : 'Emipro Technologies Pvt. Ltd.',
 'maintainer': 'Emipro Technologies',
 'summary': 'Fetch your records in fraction of seconds..!!',
 'category' : 'Tools',
 'complexity': "normal",  # easy, normal, expert
 'depends' : ['base'],
 'description': """
   This module provides facility to quick search any record based on your preferences.
""",
 'website': 'http://www.emiprotechnologies.com',
 'data': [
          'view/res_users.xml',
          'view/js_view.xml',
          'view/quick_record_search_view.xml',
          'security/ir.model.access.csv',
        ],
 'qweb': ['static/src/xml/job_search.xml', ],
 'js': ['static/src/js/job_search.js', ],
 'css': ['static/src/css/job_search.css', ],
 'installable': True,
 'images': ['static/description/main_screen.jpg'],
 'auto_install': False,
 'application' : True,

}
