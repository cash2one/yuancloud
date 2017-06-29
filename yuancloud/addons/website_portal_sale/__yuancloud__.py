{
    'name': 'Website Portal for Sales',
    'category' : 'Content Management',#‘≠∑÷¿‡'Website',
    'summary': 'Add your sales document in the frontend portal (sales order, quotations, invoices)',
    'version': '1.0',
    'description': """
Add your sales document in the frontend portal. Your customers will be able to connect to their portal to see the list (and the state) of their invoices (pdf report), sales orders and quotations (web pages).
        """,
    'website': 'http://www.yuancloud.cn/page/website',
    'depends': [
        'sale',
        'website_portal',
        'website_payment',
    ],
    'data': [
        'views/templates.xml',
    ],
    'demo': [
        'data/demo.xml'
    ],
    'installable': True,
}
