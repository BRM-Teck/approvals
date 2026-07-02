{
    'name': 'Approvals',
    'version': '19.0.1.1.0',
    'category': 'Human Resources/Approvals',
    'summary': 'Create and validate approvals',
    'description': """
        This module allows to create and validate approvals.
    """,
    'author': 'BRM',
    'depends': ['base', 'mail', 'hr', 'product'],
    'data': [
        'security/approval_security.xml',
        'security/ir.model.access.csv',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/approval_menus.xml',
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
