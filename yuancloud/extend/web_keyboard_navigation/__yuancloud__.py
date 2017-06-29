# -*- encoding: utf-8 -*-

{
    'name': 'Keyboard navigation',
    'version': '1.1',
    'category' : 'Tools',
    'description': """
    This module add some keyboard shortcuts.

    On a form, mode edit:
    Ctrl + S  :  Save the current object

    On a form, mode view:
    Ctrl + Delete      :  Delete the current object
    Ctrl + N           :  New object
    Ctrl + D           :  Duplicate the current object
    Ctrl + Z           :  Cancel the modification of current object
    Ctrl + Elico       :  Edit the current object
    Ctrl + Arrow Down  :  Next object
    Ctrl + Page Down   :  Last object
    """,
    "author": "北京山水物源科技有限公司.",
    'depends': ['web'],
    'init_xml': [],
    'data': ['web_keyboard_navigation_view.xml'],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: