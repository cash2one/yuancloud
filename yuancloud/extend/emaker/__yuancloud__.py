# -*- encoding: utf-8 -*-

{
    'name': 'eMaker',
    'version': '2.2',
    'author': 'Avalos Corp',
    'category' : 'Tools',
    'summary': 'Maker your module.',
    'depends': [
        'base_technical_features',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'wizard/module_prototyper_module_export_view.xml',
        'views/module_prototyper_view.xml',
        'views/ir_model_fields_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
