from odoo import models, fields

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[
        ('invoice', 'Invoices'),
        ('payment', 'Payments')
    ], ondelete={'invoice': 'set default', 'payment': 'set default'})
