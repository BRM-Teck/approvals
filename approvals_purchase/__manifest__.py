{
    'name': 'Validations - Achats',
    'version': '19.0.1.0.7',
    'category': 'Validations',
    'summary': "Ce module ajoute au flux de validation la possibilité de générer une demande de prix à partir d'une demande de validation d'achat.",
    'description': """
        Ce module ajoute au flux de validation la possibilité de générer une demande de prix à partir d'une demande de validation d'achat.
    """,
    'author': 'BRM',
    'license': 'OPL-1',
    'depends': ['approvals', 'purchase'],
    'data': [
        'data/approval_category_data.xml',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
