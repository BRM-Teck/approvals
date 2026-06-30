{
    'name': 'Validations - Documents',
    'version': '19.0.1.0.0',
    'category': 'Validations',
    'summary': "Intégration entre les validations et la gestion électronique de documents (GED).",
    'description': """
Validations - Documents
=======================
Ce module permet l'intégration entre le module de validations (approvals) et l'application Documents.
    """,
    'author': 'BRM-Teck',
    'website': 'https://github.com/BRM-Teck/approvals',
    'depends': ['approvals', 'documents'],
    'data': [
        'views/approval_category_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
