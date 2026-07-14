{
    'name': 'Approvals - Account',
    'version': '19.0.1.0.2',
    'category': 'Human Resources/Approvals',
    'summary': 'Link approvals with invoices and payments',
    'description': """
        This module links the Approval request to the Account Invoices and Payments.
    """,
    'author': 'BRM',
    'depends': ['approvals', 'account'],
    'data': [
        'data/approval_category_data.xml',
        'views/approval_request_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
